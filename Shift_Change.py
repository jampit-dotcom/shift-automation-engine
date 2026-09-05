import os
import datetime
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# Load variables from the local .env file
load_dotenv()

# ---------------------------------------------------------------------------
# Initialize the OpenAI client
# ---------------------------------------------------------------------------
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)
# ---------------------------------------------------------------------------
# AI Summary
# ---------------------------------------------------------------------------
def summarize_ticket_with_ai(ticket_title, ticket_description):
    #Sends a raw ticket description to the AI API and returns a concise 2-bullet executive summary.
    prompt = f"""
    You are an expert Cyber Threat Intelligence Analyst helping summarize shift logs for a SOC handoff report.
    
    Ticket Title: {ticket_title}
    Raw Description: {ticket_description}
    
    Task: Provide a concise, professional 2-sentence summary of this incident for the incoming shift analyst.
    Focus on:
    1. Root cause / trigger event.
    2. Current remediation status or immediate next action required.
    
    Do NOT include filler text. Output only the summary points.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise cybersecurity operational reporting assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # Low temperature ensures factual, consistent outputs without creative halluncinations
            max_tokens=150 # Keep response short.
        )
        summary = response.choices[0].message.content.strip()
        return summary
    
    except Exception as e:
        print(f"[!] AI API call failed for ticket '{ticket_title}': {e}")
        return "Summary unavailable (API error)."

# ---------------------------------------------------------------------------
# HTML report
# ---------------------------------------------------------------------------
def generate_html_report(dataframe, output_filename="shift_handoff_report.html"):
    """
    Takes the processed Pandas DataFrame and injects it into a styled, Dark-Mode HTML template.
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_tickets = len(dataframe)

    # Building Ticket Cards HTML Dynamically
    ticket_cards_html = ""
    for _, row in dataframe.iterrows():
        ticket_id = row.get('Ticket_ID', 'N/A')
        title = row.get('Title', 'No Title')
        status = row.get('Status', 'OPEN').upper()
        summary = row.get('AI_Shift_Summary', 'No summary available.')
        raw_desc = row.get('Description', 'No raw description provided.')

        # Set status badge color dynamically
        badge_class = "badge-open" if status == "OPEN" else "badge-closed"

        card = f"""
        <div class="ticket-card">
            <div class="ticket-header">
                <span class="ticket-id">{ticket_id}</span>
                <span class="ticket-title">{title}</span>
                <span class="badge {badge_class}">{status}</span>
            </div>
            <div class="summary-section">
                <strong>🤖 AI Handoff Executive Summary:</strong>
                <p>{summary}</p>
            </div>
            <details class="raw-details">
                <summary>View Raw Incident Logs / Full Description</summary>
                <p>{raw_desc}</p>
            </details>
        </div>
        """
        ticket_cards_html += card

    # Dark-Mode HTML & CSS Template
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SOC Shift Handoff Report</title>
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-blue: #38bdf8;
            --badge-open-bg: #991b1b;
            --badge-open-text: #fca5a5;
            --border-color: #334155;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            margin: 0;
            padding: 30px;
            display: flex;
            justify-content: center;
        }}

        .container {{
            max-width: 900px;
            width: 100%;
        }}

        .header {{
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 20px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }}

        .header h1 {{
            margin: 0;
            font-size: 28px;
            color: var(--accent-blue);
            letter-spacing: -0.5px;
        }}

        .meta-info {{
            font-size: 14px;
            color: var(--text-secondary);
            text-align: right;
        }}

        .metrics-banner {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            display: flex;
            gap: 40px;
        }}

        .metric {{
            display: flex;
            flex-direction: column;
        }}

        .metric-label {{
            font-size: 12px;
            color: var(--text-secondary);
            text-transform: uppercase;
        }}

        .metric-value {{
            font-size: 20px;
            font-weight: bold;
            color: var(--accent-blue);
        }}

        .ticket-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}

        .ticket-header {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
        }}

        .ticket-id {{
            font-family: monospace;
            background: var(--border-color);
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
            color: var(--accent-blue);
        }}

        .ticket-title {{
            font-size: 18px;
            font-weight: 600;
            flex-grow: 1;
        }}

        .badge {{
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }}

        .badge-open {{
            background-color: var(--badge-open-bg);
            color: var(--badge-open-text);
        }}

        .summary-section {{
            background-color: #0f172a;
            border-left: 4px solid var(--accent-blue);
            padding: 12px 16px;
            border-radius: 0 6px 6px 0;
            margin-bottom: 15px;
        }}

        .summary-section p {{
            margin: 5px 0 0 0;
            color: var(--text-primary);
            line-height: 1.5;
        }}

        .raw-details {{
            font-size: 13px;
            color: var(--text-secondary);
            cursor: pointer;
        }}

        .raw-details summary {{
            outline: none;
            user-select: none;
        }}

        .raw-details p {{
            margin-top: 10px;
            padding: 10px;
            background: #0f172a;
            border-radius: 4px;
            font-family: monospace;
            white-space: pre-wrap;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>SOC Shift Handoff Report</h1>
                <span style="color: var(--text-secondary); font-size: 14px;">Automated Cyber Incident Operations Summary</span>
            </div>
            <div class="meta-info">
                <div><strong>Generated:</strong> {now}</div>
                <div><strong>Classification:</strong> CTI Operational Internal</div>
            </div>
        </div>

        <div class="metrics-banner">
            <div class="metric">
                <span class="metric-label">Active Handoff Tickets</span>
                <span class="metric-value">{total_tickets}</span>
            </div>
            <div class="metric">
                <span class="metric-label">AI Processing Status</span>
                <span class="metric-value" style="color: #4ade80;">100% Complete</span>
            </div>
        </div>

        <div class="tickets-container">
            {ticket_cards_html}
        </div>
    </div>
</body>
</html>
    """

    # Write HTML output to disk
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n[🚀 SUCCESS] Shift Handoff Report generated: {os.path.abspath(output_filename)}")

# ---------------------------------------------------------------------------
# Pipeline excution 
# ---------------------------------------------------------------------------
def process_shift_handoff(csv_file_path):
    """
    Phase 1 + Phase 2 Pipeline:
    1. Reads ticket CSV
    2. Filters open tickets
    3. Iterates through tickets and appends AI summaries
    """
    if not os.path.exists(csv_file_path):
        print(f"[X] Error: File '{csv_file_path}' not found.")
        return None

    print(f"[*] Reading ticket export from: {csv_file_path}")
    df = pd.read_csv(csv_file_path)

    # Filter for active tickets if column exists
    if 'Status' in df.columns:
        active_tickets = df[df['Status'].str.upper() == 'OPEN'].copy()
    else:
        active_tickets = df.copy()

    print(f"[+] Processing {len(active_tickets)} active tickets with AI summarization...\n")

    # Array to hold generated summaries
    ai_summaries = []

    # Iterate through each row in the dataframe
    for index, row in active_tickets.iterrows():
        title = row.get('Title', 'No Title')
        description = row.get('Description', 'No Description Provided')

        print(f" -> Summarizing Ticket ID {row.get('Ticket_ID', index)}: {title}...")
        
        # Call Phase 2 AI Function
        summary = summarize_ticket_with_ai(title, description)
        ai_summaries.append(summary)

    # Add the new AI summaries as a distinct column in our Pandas Dataframe
    active_tickets['AI_Shift_Summary'] = ai_summaries

    print("\n[+] AI Summarization Complete!")
    return active_tickets


# --- EXECUTION BLOCK ---
if __name__ == "__main__":
    # Test file name
    sample_csv = r"D:\Learnimg Python\Shift Change\cybersecurity_tickets_mock.csv"
    
    # Process tickets
    summary_df = process_shift_handoff(sample_csv)

    if summary_df is not None:
        # Display the results in terminal
        print("\n=== PROCESSED SHIFT HANDOFF DATA ===")
        print(summary_df[['Ticket_ID', 'Title', 'AI_Shift_Summary']])

        generate_html_report(summary_df)
