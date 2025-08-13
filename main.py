#!/usr/bin/env python3
"""
main.py — Unified Orchestrator (uses rms_downloader.py as primary download engine) — UPDATED
"""
from __future__ import annotations
import os, sys, argparse, logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
from typing import Any, Callable, Iterable, Optional
from dotenv import load_dotenv
import glob

def _safe_import(name: str):
    try:
        module = __import__(name)
        return module, None
    except Exception as e:
        return None, e

rms_login, _imp_err_login = _safe_import("rms_login")
rms_downloader, _imp_err_downloader = _safe_import("rms_downloader")
salary_reconciliation_agent, _imp_err_reco = _safe_import("salary_reconciliation_agent")
auto_email, _imp_err_mail = _safe_import("auto_email")

IST = ZoneInfo("Asia/Kolkata")

def setup_logging(level: str = "INFO") -> None:
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(fmt); logger.addHandler(sh)
    fh = RotatingFileHandler("logs/agent.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8"); fh.setFormatter(fmt); logger.addHandler(fh)

def now_ist() -> datetime: return datetime.now(tz=IST)
def previous_month(d: date) -> tuple[int, str, int]:
    first = d.replace(day=1); prev_last = first - timedelta(days=1)
    return prev_last.month, prev_last.strftime("%B"), prev_last.year

def require_env(keys: list[str]) -> dict:
    load_dotenv()
    vals = {k: os.getenv(k) for k in keys}
    if not vals.get("RMS_USERNAME"): vals["RMS_USERNAME"] = os.getenv("RMS_USER")
    if not vals.get("RMS_PASSWORD"): vals["RMS_PASSWORD"] = os.getenv("RMS_PASS")
    if not vals.get("RMS_USERNAME") or not vals.get("RMS_PASSWORD"):
        logging.warning("RMS_USERNAME/RMS_PASSWORD not set (or RMS_USER/RMS_PASS). If downloads require login, set them in .env.")
    return vals

def action_download(salary_month_name: str | None, salary_year: int | None) -> None:
    """Download all data using rms_downloader.py functions directly"""
    t = now_ist().date()
    if not (salary_month_name and salary_year):
        _, m_name, y = previous_month(t)
        salary_month_name = salary_month_name or m_name
        salary_year = salary_year or y
    
    logging.info(f"[DOWNLOAD] Target period: {salary_month_name} {salary_year}")
    
    if rms_downloader:
        try:
            logging.info("🚀 Starting downloads via rms_downloader.py...")
            
            # Set environment variables that rms_downloader expects
            os.environ['SALARY_MONTH'] = salary_month_name
            os.environ['SALARY_YEAR'] = str(salary_year)
            
            # Create driver and login
            driver = rms_downloader.make_driver()
            if not rms_downloader.login_rms(driver, 
                                          os.getenv('RMS_USERNAME'), 
                                          os.getenv('RMS_PASSWORD')):
                logging.error("❌ Login failed")
                return
            
            try:
                # Call individual export functions
                logging.info("📊 Downloading Salary Sheet...")
                rms_downloader.export_salary_sheet(driver, salary_month_name, salary_year)
                
                logging.info("💰 Downloading TDS...")
                rms_downloader.export_tds(driver, salary_month_name, salary_year)
                
                logging.info("🏦 Downloading Bank SOA...")
                rms_downloader.export_bank_soa_for_salary_month(driver, salary_month_name, salary_year)
                
                logging.info("✅ All downloads completed successfully")
                
            finally:
                driver.quit()
                
        except Exception as e:
            logging.error(f"❌ rms_downloader.py failed: {e}")
    else:
        logging.error("❌ rms_downloader.py module not available")

    logging.info("Download step completed.")

def action_reconcile() -> str:
    """Run reconciliation using salary_reconciliation_agent.py"""
    if salary_reconciliation_agent:
        reco_fn = None
        for fn_name in ["perform_reconciliation", "run_reconciliation", "main"]:
            if hasattr(salary_reconciliation_agent, fn_name):
                reco_fn = getattr(salary_reconciliation_agent, fn_name)
                break
        
        if not reco_fn:
            raise RuntimeError("No reconciliation entrypoint found in salary_reconciliation_agent.py")
        
        logging.info("Starting reconciliation…")
        try:
            result = reco_fn()
        except Exception as e:
            logging.error(f"Reconciliation failed: {e}")
            return ""
        
        # Look for output files
        month = now_ist().strftime("%B")
        year = now_ist().year
        
        candidates = [
            os.path.join("output", f"Salary_Reconciliation_Report_{month}_{year}.xlsx"),
            os.path.join("SalaryReports", now_ist().strftime("%Y-%m-%d"), "reconciliation_result.xlsx"),
            f"Salary_Reconciliation_Report_{month}_{year}.xlsx"
        ]
        
        out_path = next((p for p in candidates if os.path.exists(p)), "")
        if out_path:
            logging.info(f"Reconciliation report: {out_path}")
        else:
            logging.warning("Reconciliation finished, but report path not found in common locations.")
        
        return out_path or (result if isinstance(result, str) else "")
    else:
        logging.error("❌ salary_reconciliation_agent module not available")
        return ""

def action_email() -> None:
    """Send reconciliation email using auto_email.py"""
    if auto_email:
        mail_fn = None
        for fn_name in ["send_email", "main", "run"]:
            if hasattr(auto_email, fn_name):
                mail_fn = getattr(auto_email, fn_name)
                break
        
        if not mail_fn:
            raise RuntimeError("No email entrypoint found in auto_email.py")
        
        logging.info("Sending reconciliation email…")
        try:
            mail_fn()
            logging.info("Email step completed.")
        except Exception as e:
            logging.error(f"Email sending failed: {e}")
    else:
        logging.error("❌ auto_email module not available")

def action_all(month_name: str | None, year: int | None, skip_download: bool = False) -> None:
    """Run the complete workflow: download → reconcile → email"""
    logging.info(f"Starting complete workflow for {month_name or 'previous month'} {year or 'auto-detect year'}")
    
    try:
        # Step 1: Download (unless skipped)
        if not skip_download:
            logging.info("Step 1: Downloading data...")
            action_download(month_name, year)
        else:
            logging.info("Step 1: Download skipped as requested")
        
        # Step 2: Reconciliation
        logging.info("Step 2: Running reconciliation...")
        report_path = action_reconcile()
        if report_path:
            logging.info(f"✅ Reconciliation completed: {report_path}")
        
        # Step 3: Email
        logging.info("Step 3: Sending email...")
        action_email()
        
        logging.info("✅ Complete workflow finished successfully!")
        
    except Exception as e:
        logging.error(f"❌ Workflow failed at some step: {str(e)}")
        raise e

def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Salary Reconciliation Agent Orchestrator (uses rms_downloader.py)")
    sub = p.add_subparsers(dest="command", required=False)
    p_dl = sub.add_parser("download", help="Download Salary, TDS, Bank SOA for the given/previous month")
    p_dl.add_argument("--month-name", help="Month name, e.g., July")
    p_dl.add_argument("--year", type=int, help="Four-digit year, e.g., 2025")
    sub.add_parser("reconcile", help="Run reconciliation (salary_reconciliation_agent.py)")
    sub.add_parser("email", help="Send the final reconciliation email (auto_email.py)")
    p_all = sub.add_parser("all", help="Run download → reconcile → email")
    p_all.add_argument("--month-name", help="Month name, e.g., July")
    p_all.add_argument("--year", type=int, help="Four-digit year, e.g., 2025")
    p_all.add_argument("--skip-download", action="store_true", help="Skip download step")
    p.add_argument("--log-level", default="INFO", help="DEBUG, INFO, WARNING, ERROR")
    return p.parse_args(argv)

def main(argv: list[str]) -> int:
    args = parse_args(argv)
    setup_logging(args.log_level)
    cmd = getattr(args, "command", None) or "all"
    logging.info(f"Command: {cmd}")
    
    try:
        if cmd == "download":
            month_name = getattr(args, "month_name", None)
            year = getattr(args, "year", None)
            action_download(month_name, year)
        elif cmd == "reconcile":
            action_reconcile()
        elif cmd == "email":
            action_email()
        elif cmd == "all":
            month_name = getattr(args, "month_name", None)
            year = getattr(args, "year", None)
            skip_download = getattr(args, "skip_download", False)
            action_all(month_name, year, skip_download)
        else:
            logging.error(f"Unknown command: {cmd}")
            return 2
        return 0
    except Exception:
        logging.exception("Fatal error")
        return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
