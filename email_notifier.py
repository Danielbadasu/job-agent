import smtplib
import json
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# ── EMAIL CONFIG ────────────────────────────────────────────────────────────
from config import GMAIL_USER, GMAIL_PASSWORD, NOTIFY_EMAIL


def send_report():
    """Read application_queue.json and send daily report email"""

    # Load results
    if not os.path.exists("application_queue.json"):
        print("❌ application_queue.json not found — skipping email")
        return

    with open("application_queue.json") as f:
        queue = json.load(f)

    today = datetime.now().strftime("%A, %B %d %Y")
    time  = datetime.now().strftime("%I:%M %p")
    count = len(queue)

    # ── BUILD EMAIL BODY ────────────────────────────────────────────────────
    job_lines = ""
    for i, job in enumerate(queue, 1):
        score = job.get("score", "N/A")
        company = job.get("company", "").upper()
        title = job.get("title", "")
        url = job.get("url", "")
        resume = os.path.basename(job.get("resume_pdf", ""))
        cover = os.path.basename(job.get("cover_letter_pdf", ""))

        job_lines += f"""
<tr style="background: {'#f9f9f9' if i % 2 == 0 else '#ffffff'};">
  <td style="padding:10px; font-weight:bold; color:#2E5090;">{score}%</td>
  <td style="padding:10px; font-weight:bold;">{company}</td>
  <td style="padding:10px;">{title}</td>
  <td style="padding:10px;">
    <a href="{url}" style="color:#2E5090; text-decoration:none;">Apply Now →</a>
  </td>
  <td style="padding:10px; font-size:12px; color:#666;">
    📄 {resume}<br>✉️ {cover}
  </td>
</tr>"""

    html = f"""
<!DOCTYPE html>
<html>
<body style="font-family: Calibri, Arial, sans-serif; margin:0; padding:0; background:#f4f4f4;">

  <div style="max-width:700px; margin:30px auto; background:#ffffff; border-radius:8px; overflow:hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">

    <!-- HEADER -->
    <div style="background: linear-gradient(135deg, #1F3864, #2E5090); padding:30px; text-align:center;">
      <h1 style="color:#ffffff; margin:0; font-size:24px;">🎯 Job Agent Daily Report</h1>
      <p style="color:#a8c4e0; margin:8px 0 0 0;">{today} at {time}</p>
    </div>

    <!-- STATS -->
    <div style="display:flex; padding:20px; background:#f0f4ff; border-bottom:2px solid #e0e8ff;">
      <div style="flex:1; text-align:center;">
        <div style="font-size:32px; font-weight:bold; color:#2E5090;">{count}</div>
        <div style="font-size:13px; color:#666;">Jobs Matched</div>
      </div>
      <div style="flex:1; text-align:center;">
        <div style="font-size:32px; font-weight:bold; color:#2E5090;">{count}</div>
        <div style="font-size:13px; color:#666;">Resumes Ready</div>
      </div>
      <div style="flex:1; text-align:center;">
        <div style="font-size:32px; font-weight:bold; color:#2E5090;">{count}</div>
        <div style="font-size:13px; color:#666;">Cover Letters Ready</div>
      </div>
    </div>

    <!-- JOBS TABLE -->
    <div style="padding:25px;">
      <h2 style="color:#1F3864; margin-top:0; border-bottom:2px solid #2E5090; padding-bottom:10px;">
        🏆 Top Matches — Ready to Apply
      </h2>

      <table style="width:100%; border-collapse:collapse; font-size:14px;">
        <thead>
          <tr style="background:#1F3864; color:#ffffff;">
            <th style="padding:10px; text-align:left;">Score</th>
            <th style="padding:10px; text-align:left;">Company</th>
            <th style="padding:10px; text-align:left;">Role</th>
            <th style="padding:10px; text-align:left;">Link</th>
            <th style="padding:10px; text-align:left;">Files</th>
          </tr>
        </thead>
        <tbody>
          {job_lines}
        </tbody>
      </table>
    </div>

    <!-- INSTRUCTIONS -->
    <div style="padding:20px 25px; background:#f0f4ff; border-top:1px solid #e0e8ff;">
      <h3 style="color:#1F3864; margin-top:0;">📋 What to do now:</h3>
      <ol style="color:#444; line-height:1.8;">
        <li>Open <strong>D:\\job_agent\\tailored_resumes\\</strong> on your PC</li>
        <li>Click each <strong>Apply Now</strong> link above</li>
        <li>Upload the matching <strong>Resume PDF</strong> and <strong>Cover Letter PDF</strong></li>
        <li>Submit — you're done! 🎯</li>
      </ol>
    </div>

    <!-- FOOTER -->
    <div style="padding:15px; text-align:center; background:#1F3864;">
      <p style="color:#a8c4e0; margin:0; font-size:12px;">
        Job Application Agent • Running automatically every morning • 
        <strong style="color:#ffffff;">GO GET THOSE INTERVIEWS! 💪</strong>
      </p>
    </div>

  </div>
</body>
</html>
"""

    # ── SEND EMAIL ──────────────────────────────────────────────────────────
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🎯 Job Agent — {count} Applications Ready [{today}]"
    msg["From"]    = GMAIL_USER
    msg["To"]      = NOTIFY_EMAIL

    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, NOTIFY_EMAIL, msg.as_string())
        print(f"✅ Report emailed to {NOTIFY_EMAIL}")
    except Exception as e:
        print(f"❌ Email failed: {e}")


if __name__ == "__main__":
    send_report()
