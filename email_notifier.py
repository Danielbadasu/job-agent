import smtplib
import json
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from config import GMAIL_USER, GMAIL_PASSWORD, NOTIFY_EMAIL


def send_report():
    if not os.path.exists("application_queue.json"):
        print("❌ application_queue.json not found — skipping email")
        return

    with open("application_queue.json") as f:
        queue = json.load(f)

    if not queue:
        print("⚠️  No jobs in queue — skipping email")
        return

    today = datetime.now().strftime("%A, %B %d %Y")
    time  = datetime.now().strftime("%I:%M %p")
    count = len(queue)

    # ── BUILD JOB ROWS ──────────────────────────────────────────────────────
    job_lines = ""
    for i, job in enumerate(queue, 1):
        score    = job.get("score", "N/A")
        company  = job.get("company", "").upper()
        title    = job.get("title", "")
        url      = job.get("url", "")
        resume   = os.path.basename(job.get("resume_pdf", ""))
        cover    = os.path.basename(job.get("cover_letter_pdf", ""))

        job_lines += f"""
<tr style="background: {'#f9f9f9' if i % 2 == 0 else '#ffffff'};">
  <td style="padding:10px; font-weight:bold; color:#2E5090; font-size:16px;">{score}%</td>
  <td style="padding:10px; font-weight:bold;">{company}</td>
  <td style="padding:10px;">{title}</td>
  <td style="padding:10px;">
    <a href="{url}" style="background:#2E5090; color:#ffffff; padding:6px 12px; border-radius:4px; text-decoration:none; font-size:12px;">Apply Now →</a>
  </td>
  <td style="padding:10px; font-size:11px; color:#666;">
    📄 {resume}<br>✉️ {cover}
  </td>
</tr>"""

    html = f"""
<!DOCTYPE html>
<html>
<body style="font-family: Calibri, Arial, sans-serif; margin:0; padding:0; background:#f4f4f4;">
  <div style="max-width:750px; margin:30px auto; background:#ffffff; border-radius:8px; overflow:hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">

    <div style="background: linear-gradient(135deg, #1F3864, #2E5090); padding:30px; text-align:center;">
      <h1 style="color:#ffffff; margin:0; font-size:26px;">🎯 Job Agent Daily Report</h1>
      <p style="color:#a8c4e0; margin:8px 0 0 0; font-size:14px;">{today} at {time}</p>
    </div>

    <div style="display:flex; padding:20px; background:#f0f4ff; border-bottom:2px solid #e0e8ff; text-align:center;">
      <div style="flex:1;">
        <div style="font-size:36px; font-weight:bold; color:#2E5090;">{count}</div>
        <div style="font-size:13px; color:#666;">Jobs Matched</div>
      </div>
      <div style="flex:1;">
        <div style="font-size:36px; font-weight:bold; color:#2E5090;">{count}</div>
        <div style="font-size:13px; color:#666;">Resumes Ready</div>
      </div>
      <div style="flex:1;">
        <div style="font-size:36px; font-weight:bold; color:#2E5090;">{count}</div>
        <div style="font-size:13px; color:#666;">Cover Letters Ready</div>
      </div>
    </div>

    <div style="padding:25px;">
      <h2 style="color:#1F3864; margin-top:0; border-bottom:2px solid #2E5090; padding-bottom:10px;">
        🏆 Top Matches — PDFs Attached!
      </h2>
      <table style="width:100%; border-collapse:collapse; font-size:13px;">
        <thead>
          <tr style="background:#1F3864; color:#ffffff;">
            <th style="padding:10px; text-align:left;">Score</th>
            <th style="padding:10px; text-align:left;">Company</th>
            <th style="padding:10px; text-align:left;">Role</th>
            <th style="padding:10px; text-align:left;">Link</th>
            <th style="padding:10px; text-align:left;">Files</th>
          </tr>
        </thead>
        <tbody>{job_lines}</tbody>
      </table>
    </div>

    <div style="padding:20px 25px; background:#f0f4ff; border-top:1px solid #e0e8ff;">
      <h3 style="color:#1F3864; margin-top:0;">📋 What to do now:</h3>
      <ol style="color:#444; line-height:2;">
        <li>Click each <strong>Apply Now</strong> button above</li>
        <li>Upload the matching <strong>Resume PDF</strong> attached to this email</li>
        <li>Upload the matching <strong>Cover Letter PDF</strong> attached to this email</li>
        <li>Submit — you're done! 🎯</li>
      </ol>
    </div>

    <div style="padding:15px; text-align:center; background:#1F3864;">
      <p style="color:#a8c4e0; margin:0; font-size:12px;">
        Job Application Agent • Runs automatically every morning at 7:00 AM •
        <strong style="color:#ffffff;">GO GET THOSE INTERVIEWS! 💪</strong>
      </p>
    </div>

  </div>
</body>
</html>"""

    # ── BUILD EMAIL ──────────────────────────────────────────────────────────
    msg = MIMEMultipart("mixed")
    msg["Subject"] = f"🎯 Job Agent — {count} Applications Ready + PDFs [{today}]"
    msg["From"]    = GMAIL_USER
    msg["To"]      = NOTIFY_EMAIL
    msg.attach(MIMEText(html, "html"))

    # ── ATTACH PDFs ──────────────────────────────────────────────────────────
    attached = 0
    for job in queue:
        for key in ["resume_pdf", "cover_letter_pdf"]:
            pdf_path = job.get(key, "")
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                filename = os.path.basename(pdf_path)
                part.add_header("Content-Disposition", f"attachment; filename={filename}")
                msg.attach(part)
                attached += 1

    print(f"📎 Attaching {attached} PDFs to email...")

    # ── SEND ─────────────────────────────────────────────────────────────────
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, NOTIFY_EMAIL, msg.as_string())
        print(f"✅ Report + {attached} PDFs emailed to {NOTIFY_EMAIL}")
    except Exception as e:
        print(f"❌ Email failed: {e}")


if __name__ == "__main__":
    send_report()
