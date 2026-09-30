#!/usr/bin/env python3
"""
Generator for 3 PPT-Ready Technical Diagrams (Redesigned Version):
1. Data Flow Diagram (DATA FLOW AND MODEL ADAPTATION)
2. Control Flow Diagram (CONTROL FLOW OF CONTINUOUS MONITORING)
3. Sequence Flow Diagram (SEQUENCE OF CONTINUOUS MODEL MONITORING)

Human-made PowerPoint academic visual layout, exact project ensembling logic,
high-resolution 300 DPI PNG and vector SVG outputs.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Output directory
OUTPUT_DIR = "/Users/sam/Desktop/Major1/Documentation/diagrams"
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['font.family'] = 'sans-serif'

# Color Palette (Clean Academic Presentation Style)
BG_COLOR = '#FFFFFF'
CARD_BG = '#FFFFFF'
BORDER_DARK = '#1E293B'
TEXT_DARK = '#0F172A'
TEXT_MUTED = '#475569'

COLOR_BLUE_BG = '#F0F9FF'
COLOR_BLUE_BORDER = '#0284C7'
COLOR_BLUE_TEXT = '#0369A1'

COLOR_GREEN_BG = '#F0FDF4'
COLOR_GREEN_BORDER = '#16A34A'
COLOR_GREEN_TEXT = '#15803D'

COLOR_YELLOW_BG = '#FFFBEB'
COLOR_YELLOW_BORDER = '#D97706'
COLOR_YELLOW_TEXT = '#B45309'

COLOR_RED_BG = '#FEF2F2'
COLOR_RED_BORDER = '#DC2626'
COLOR_RED_TEXT = '#B91C1C'

ARROW_DEFAULT = '#334155'


def draw_box(ax, x, y, width, height, text, bg_color=CARD_BG, border_color=BORDER_DARK, text_color=TEXT_DARK, fontsize=10.5, fontweight='bold', boxstyle="round,pad=0.35,rounding_size=0.12"):
    """Draws a clean rounded rectangular box with centered text."""
    p_box = patches.FancyBboxPatch(
        (x, y), width, height,
        boxstyle=boxstyle,
        facecolor=bg_color,
        edgecolor=border_color,
        linewidth=1.8,
        zorder=3
    )
    ax.add_patch(p_box)
    ax.text(
        x + width / 2.0, y + height / 2.0, text,
        ha='center', va='center',
        fontsize=fontsize, fontweight=fontweight,
        color=text_color, zorder=4,
        wrap=True
    )


def draw_diamond(ax, cx, cy, width, height, text, bg_color='#EFF6FF', border_color=BORDER_DARK, text_color=TEXT_DARK, fontsize=10.5, fontweight='bold'):
    """Draws a decision diamond with centered text."""
    hw = width / 2.0
    hh = height / 2.0
    pts = [[cx, cy + hh], [cx + hw, cy], [cx, cy - hh], [cx - hw, cy]]
    diamond = patches.Polygon(pts, closed=True, facecolor=bg_color, edgecolor=border_color, linewidth=1.8, zorder=3)
    ax.add_patch(diamond)
    ax.text(
        cx, cy, text,
        ha='center', va='center',
        fontsize=fontsize, fontweight=fontweight,
        color=text_color, zorder=4,
        wrap=True
    )


def draw_arrow(ax, x1, y1, x2, y2, color=ARROW_DEFAULT, width=1.8, label=None, label_pos=0.5, fontsize=9.5, text_color=TEXT_MUTED, label_bg='#FFFFFF'):
    """Draws a straight line arrow with optional centered text label."""
    ax.annotate(
        '', xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle='-|>',
            color=color,
            lw=width,
            mutation_scale=13,
            shrinkA=0, shrinkB=0
        ),
        zorder=2
    )
    if label:
        lx = x1 + (x2 - x1) * label_pos
        ly = y1 + (y2 - y1) * label_pos
        ax.text(
            lx, ly + 0.12, label,
            ha='center', va='center',
            fontsize=fontsize, fontweight='bold',
            color=text_color, zorder=5,
            bbox=dict(boxstyle='round,pad=0.2', facecolor=label_bg, edgecolor='none', alpha=0.95)
        )


# ==========================================
# DIAGRAM 1: DATA FLOW DIAGRAM
# ==========================================
def generate_data_flow_diagram():
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis('off')

    # Main Title
    ax.text(8, 8.5, "DATA FLOW AND MODEL ADAPTATION", ha='center', va='center', fontsize=19, fontweight='bold', color=TEXT_DARK)

    # -------------------------------------------------------------
    # SECTION 1: HISTORICAL MODEL TRAINING (TOP)
    # -------------------------------------------------------------
    s1_bg = patches.FancyBboxPatch((0.5, 6.0), 15.0, 1.9, boxstyle="round,pad=0.1,rounding_size=0.08", facecolor='#F8FAFC', edgecolor='#CBD5E1', lw=1.5, zorder=1)
    ax.add_patch(s1_bg)
    ax.text(0.8, 7.55, "SECTION 1: HISTORICAL MODEL TRAINING", fontsize=11, fontweight='bold', color='#334155', zorder=2)

    s1_boxes = [
        "Historical\nTransaction Data",
        "Data\nPreprocessing",
        "Global Model\nTraining",
        "Static Global\nModel"
    ]
    s1_xs = [0.9, 4.6, 8.3, 12.0]
    box_w, box_h = 3.1, 1.05
    y_s1 = 6.25

    for i, title in enumerate(s1_boxes):
        draw_box(ax, s1_xs[i], y_s1, box_w, box_h, title, bg_color='#FFFFFF', border_color='#0284C7', text_color='#0369A1', fontsize=10.5)
        if i < len(s1_boxes) - 1:
            draw_arrow(ax, s1_xs[i] + box_w, y_s1 + box_h/2, s1_xs[i+1], y_s1 + box_h/2, color='#0284C7', width=1.8)

    # -------------------------------------------------------------
    # SECTION 2: CONTINUOUS PRODUCTION MONITORING (BOTTOM)
    # -------------------------------------------------------------
    s2_bg = patches.FancyBboxPatch((0.5, 0.4), 15.0, 5.2, boxstyle="round,pad=0.1,rounding_size=0.08", facecolor='#F8FAFC', edgecolor='#CBD5E1', lw=1.5, zorder=1)
    ax.add_patch(s2_bg)
    ax.text(0.8, 5.25, "SECTION 2: CONTINUOUS PRODUCTION MONITORING", fontsize=11, fontweight='bold', color='#334155', zorder=2)

    s2_top_boxes = [
        "Incoming\nProduction Data",
        "Batch\nProcessing",
        "Data Validation\n& Preprocessing",
        "KS Drift\nDetection",
        "3-Tier Decision\nEngine"
    ]
    s2_xs = [0.8, 3.8, 6.8, 9.8, 12.8]
    w2, h2 = 2.4, 0.95
    y_s2_top = 4.15

    for i, title in enumerate(s2_top_boxes):
        border_c = '#0284C7' if i < 4 else BORDER_DARK
        draw_box(ax, s2_xs[i], y_s2_top, w2, h2, title, bg_color='#FFFFFF', border_color=border_c, text_color=TEXT_DARK, fontsize=10)
        if i < len(s2_top_boxes) - 1:
            draw_arrow(ax, s2_xs[i] + w2, y_s2_top + h2/2, s2_xs[i+1], y_s2_top + h2/2, color='#0284C7', width=1.8)

    # Static Global Model Connection to Decision Engine / Ensemble
    # Feed arrow down from Static Global Model (S1) to Decision Engine area
    # ax.plot([13.55, 13.55], [6.25, 5.1], color='#0284C7', linestyle='--', lw=1.5, zorder=2)

    # Three Decision Outcomes from 3-Tier Decision Engine
    dec_cx = s2_xs[4] + w2 / 2.0  # 14.0
    dec_bottom_y = y_s2_top  # 4.15

    # Trunk line down from Decision Engine
    ax.plot([dec_cx, dec_cx], [dec_bottom_y, 3.3], color=BORDER_DARK, lw=1.8, zorder=2)

    # Branch distributor at y=3.3
    # GREEN at x=1.5, YELLOW at x=4.8, RED at x=8.1
    ax.plot([1.8, dec_cx], [3.3, 3.3], color=BORDER_DARK, lw=1.8, zorder=2)

    # GREEN OUTCOME
    draw_arrow(ax, 1.8, 3.3, 1.8, 2.7, color=COLOR_GREEN_BORDER, width=1.8)
    draw_box(ax, 0.8, 2.1, 2.0, 0.6, "GREEN", bg_color=COLOR_GREEN_BG, border_color=COLOR_GREEN_BORDER, text_color=COLOR_GREEN_TEXT, fontsize=11, fontweight='bold')
    draw_arrow(ax, 1.8, 2.1, 1.8, 1.5, color=COLOR_GREEN_BORDER, width=1.8)
    draw_box(ax, 0.6, 0.9, 2.4, 0.6, "Continue Monitoring", bg_color=COLOR_GREEN_BG, border_color=COLOR_GREEN_BORDER, text_color=COLOR_GREEN_TEXT, fontsize=10)

    # YELLOW OUTCOME
    draw_arrow(ax, 5.4, 3.3, 5.4, 2.7, color=COLOR_YELLOW_BORDER, width=1.8)
    draw_box(ax, 4.4, 2.1, 2.0, 0.6, "YELLOW", bg_color=COLOR_YELLOW_BG, border_color=COLOR_YELLOW_BORDER, text_color=COLOR_YELLOW_TEXT, fontsize=11, fontweight='bold')
    draw_arrow(ax, 5.4, 2.1, 5.4, 1.7, color=COLOR_YELLOW_BORDER, width=1.8)
    draw_box(ax, 4.4, 1.1, 2.0, 0.6, "Warning", bg_color=COLOR_YELLOW_BG, border_color=COLOR_YELLOW_BORDER, text_color=COLOR_YELLOW_TEXT, fontsize=10)

    # Merge Yellow down to Continue Monitoring
    draw_arrow(ax, 5.4, 1.1, 5.4, 0.6, color=COLOR_YELLOW_BORDER, width=1.8)
    ax.plot([3.0, 5.4], [0.6, 0.6], color=COLOR_GREEN_BORDER, lw=1.8, zorder=2)
    # Merged Continue Monitoring -> Next Batch
    draw_box(ax, 0.6, 0.45, 2.4, 0.45, "Next Production Batch", bg_color=COLOR_BLUE_BG, border_color=COLOR_BLUE_BORDER, text_color=COLOR_BLUE_TEXT, fontsize=9.5, fontweight='bold')
    draw_arrow(ax, 1.8, 0.9, 1.8, 0.9, color=COLOR_GREEN_BORDER, width=1.8)

    # RED OUTCOME
    draw_arrow(ax, 9.0, 3.3, 9.0, 2.7, color=COLOR_RED_BORDER, width=1.8)
    draw_box(ax, 8.0, 2.1, 2.0, 0.6, "RED", bg_color=COLOR_RED_BG, border_color=COLOR_RED_BORDER, text_color=COLOR_RED_TEXT, fontsize=11, fontweight='bold')
    draw_arrow(ax, 9.0, 2.1, 9.0, 1.6, color=COLOR_RED_BORDER, width=1.8)

    red_seq_boxes = [
        "Local Model\nRetraining",
        "Global-Local\nEnsemble",
        "Fraud\nPrediction",
        "Monitoring\nDashboard"
    ]
    red_xs = [7.5, 9.7, 11.9, 14.1]
    rw, rh = 1.75, 0.75
    y_red_seq = 0.85

    for idx, r_title in enumerate(red_seq_boxes):
        draw_box(ax, red_xs[idx], y_red_seq, rw, rh, r_title, bg_color=COLOR_RED_BG, border_color=COLOR_RED_BORDER, text_color=COLOR_RED_TEXT, fontsize=9.5, fontweight='bold')
        if idx < len(red_seq_boxes) - 1:
            draw_arrow(ax, red_xs[idx] + rw, y_red_seq + rh/2, red_xs[idx+1], y_red_seq + rh/2, color=COLOR_RED_BORDER, width=1.8)

    # Monitoring loop back arrow to Next Production Batch (from Green/Yellow merge at x=0.6)
    # Loop back line from x=0.6 to top incoming production batch x=0.8
    ax.plot([0.6, 0.4], [0.675, 0.675], color='#0284C7', lw=1.5, zorder=2)
    ax.plot([0.4, 0.4], [0.675, 4.625], color='#0284C7', lw=1.5, zorder=2)
    draw_arrow(ax, 0.4, 4.625, 0.8, 4.625, color='#0284C7', width=1.5)

    plt.tight_layout()
    png_path = os.path.join(OUTPUT_DIR, "01_data_flow_diagram.png")
    svg_path = os.path.join(OUTPUT_DIR, "01_data_flow_diagram.svg")
    plt.savefig(png_path, dpi=300, bbox_inches='tight')
    plt.savefig(svg_path, bbox_inches='tight')
    plt.close()
    print(f"Saved: {png_path} and {svg_path}")


# ==========================================
# DIAGRAM 2: CONTROL FLOW DIAGRAM
# ==========================================
def generate_control_flow_diagram():
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis('off')

    # Main Title
    ax.text(8, 8.5, "CONTROL FLOW OF CONTINUOUS MONITORING", ha='center', va='center', fontsize=19, fontweight='bold', color=TEXT_DARK)

    # 1. START node
    start_x, start_y = 1.2, 7.3
    start_w, start_h = 1.6, 0.6
    draw_box(ax, start_x, start_y, start_w, start_h, "START", bg_color='#1E293B', border_color='#1E293B', text_color='#FFFFFF', fontsize=11, fontweight='bold', boxstyle="round,pad=0.3,rounding_size=0.3")

    # Main vertical process boxes
    box_w, box_h = 3.6, 0.7
    center_x = 0.2

    vertical_steps = [
        "Incoming Production Batch",
        "Validate & Preprocess",
        "Drift Detection",
        "Evaluate Performance"
    ]
    
    y_positions = [6.2, 5.1, 4.0, 2.9]

    draw_arrow(ax, start_x + start_w/2, start_y, start_x + start_w/2, y_positions[0] + box_h, color=BORDER_DARK, width=1.8)

    for i, step_text in enumerate(vertical_steps):
        bg_c = '#FFFFFF'
        border_c = '#0284C7' if i == 0 else BORDER_DARK
        draw_box(ax, center_x + 1.0, y_positions[i], box_w, box_h, step_text, bg_color=bg_c, border_color=border_c, text_color=TEXT_DARK, fontsize=10.5, fontweight='bold')
        if i < len(vertical_steps) - 1:
            draw_arrow(ax, center_x + 1.0 + box_w/2, y_positions[i], center_x + 1.0 + box_w/2, y_positions[i+1] + box_h, color=BORDER_DARK, width=1.8)

    # Arrow down to 3-Tier Decision Diamond
    diamond_cx = center_x + 1.0 + box_w/2  # 3.0
    diamond_cy = 1.6
    draw_arrow(ax, diamond_cx, y_positions[3], diamond_cx, diamond_cy + 0.55, color=BORDER_DARK, width=1.8)

    # Single Decision Diamond
    draw_diamond(ax, diamond_cx, diamond_cy, 2.8, 1.1, "3-Tier Decision", bg_color='#EFF6FF', border_color=BORDER_DARK, text_color=TEXT_DARK, fontsize=10.5, fontweight='bold')

    # Three Branch Distributor lines from Diamond
    # GREEN (Up/Left), YELLOW (Middle), RED (Right)
    # Horizontal line from diamond right corner at x = 4.4 to x = 5.2
    ax.plot([4.4, 5.2], [diamond_cy, diamond_cy], color=BORDER_DARK, lw=1.8, zorder=2)
    # Vertical distributor line at x = 5.2 from y = 6.2 down to y = 1.0
    ax.plot([5.2, 5.2], [1.0, 6.2], color=BORDER_DARK, lw=1.8, zorder=2)

    # --- GREEN BRANCH (y = 6.2) ---
    draw_arrow(ax, 5.2, 6.2, 6.0, 6.2, color=COLOR_GREEN_BORDER, width=1.8)
    draw_box(ax, 6.0, 5.9, 1.6, 0.6, "GREEN", bg_color=COLOR_GREEN_BG, border_color=COLOR_GREEN_BORDER, text_color=COLOR_GREEN_TEXT, fontsize=10.5, fontweight='bold')
    draw_arrow(ax, 7.6, 6.2, 8.4, 6.2, color=COLOR_GREEN_BORDER, width=1.8)
    draw_box(ax, 8.4, 5.9, 3.2, 0.6, "Continue Monitoring", bg_color=COLOR_GREEN_BG, border_color=COLOR_GREEN_BORDER, text_color=COLOR_GREEN_TEXT, fontsize=10.5)

    # --- YELLOW BRANCH (y = 3.6) ---
    draw_arrow(ax, 5.2, 3.6, 6.0, 3.6, color=COLOR_YELLOW_BORDER, width=1.8)
    draw_box(ax, 6.0, 3.3, 1.6, 0.6, "YELLOW", bg_color=COLOR_YELLOW_BG, border_color=COLOR_YELLOW_BORDER, text_color=COLOR_YELLOW_TEXT, fontsize=10.5, fontweight='bold')
    draw_arrow(ax, 7.6, 3.6, 8.4, 3.6, color=COLOR_YELLOW_BORDER, width=1.8)
    draw_box(ax, 8.4, 3.3, 1.8, 0.6, "Warning", bg_color=COLOR_YELLOW_BG, border_color=COLOR_YELLOW_BORDER, text_color=COLOR_YELLOW_TEXT, fontsize=10.5)
    draw_arrow(ax, 10.2, 3.6, 10.8, 3.6, color=COLOR_YELLOW_BORDER, width=1.8)
    draw_box(ax, 10.8, 3.3, 2.6, 0.6, "Continue Monitoring", bg_color=COLOR_YELLOW_BG, border_color=COLOR_YELLOW_BORDER, text_color=COLOR_YELLOW_TEXT, fontsize=10)

    # --- RED BRANCH (y = 1.0) ---
    draw_arrow(ax, 5.2, 1.0, 6.0, 1.0, color=COLOR_RED_BORDER, width=1.8)
    draw_box(ax, 6.0, 0.7, 1.4, 0.6, "RED", bg_color=COLOR_RED_BG, border_color=COLOR_RED_BORDER, text_color=COLOR_RED_TEXT, fontsize=10.5, fontweight='bold')
    
    red_steps = [
        "Retrain Local Model",
        "Global-Local Ensemble",
        "Fraud Prediction",
        "Monitoring Dashboard"
    ]
    red_xs = [7.8, 9.9, 12.0, 14.1]
    rw, rh = 1.9, 0.6

    draw_arrow(ax, 7.4, 1.0, red_xs[0], 1.0, color=COLOR_RED_BORDER, width=1.8)

    for idx, r_text in enumerate(red_steps):
        draw_box(ax, red_xs[idx], 0.7, rw, rh, r_text, bg_color=COLOR_RED_BG, border_color=COLOR_RED_BORDER, text_color=COLOR_RED_TEXT, fontsize=9.5, fontweight='bold')
        if idx < len(red_steps) - 1:
            draw_arrow(ax, red_xs[idx] + rw, 1.0, red_xs[idx+1], 1.0, color=COLOR_RED_BORDER, width=1.8)

    # Merge Loop-Back Line
    # Join Green (x=11.6, y=6.2), Yellow (x=13.4, y=3.6), Red (x=15.0, y=1.0) at right side x = 15.6
    ax.plot([11.6, 15.4], [6.2, 6.2], color=BORDER_DARK, lw=1.5, zorder=2)
    ax.plot([13.4, 15.4], [3.6, 3.6], color=BORDER_DARK, lw=1.5, zorder=2)
    ax.plot([15.0, 15.4], [1.0, 1.0], color=BORDER_DARK, lw=1.5, zorder=2)
    ax.plot([15.4, 15.4], [1.0, 7.8], color=BORDER_DARK, lw=1.5, zorder=2)

    # Next Production Batch box at top loop x = 8.0, y = 7.5
    draw_box(ax, 6.5, 7.5, 4.2, 0.6, "Next Production Batch", bg_color=COLOR_BLUE_BG, border_color=COLOR_BLUE_BORDER, text_color=COLOR_BLUE_TEXT, fontsize=10.5, fontweight='bold')
    
    # Loop return arrows
    draw_arrow(ax, 15.4, 7.8, 10.7, 7.8, color='#0284C7', width=1.8)
    draw_arrow(ax, 6.5, 7.8, 2.8, 7.8, color='#0284C7', width=1.8)
    draw_arrow(ax, 2.8, 7.8, 2.8, 6.9, color='#0284C7', width=1.8)

    plt.tight_layout()
    png_path = os.path.join(OUTPUT_DIR, "02_control_flow_diagram.png")
    svg_path = os.path.join(OUTPUT_DIR, "02_control_flow_diagram.svg")
    plt.savefig(png_path, dpi=300, bbox_inches='tight')
    plt.savefig(svg_path, bbox_inches='tight')
    plt.close()
    print(f"Saved: {png_path} and {svg_path}")


# ==========================================
# DIAGRAM 3: SEQUENCE FLOW DIAGRAM
# ==========================================
def generate_sequence_diagram():
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis('off')

    # Main Title
    ax.text(8, 8.5, "SEQUENCE OF CONTINUOUS MODEL MONITORING", ha='center', va='center', fontsize=19, fontweight='bold', color=TEXT_DARK)

    # 7 Participants horizontally at top
    participants = [
        "Production\nData",
        "Monitoring\nSystem",
        "Drift\nDetector",
        "Decision\nEngine",
        "Local\nModel",
        "Global-Local\nEnsemble",
        "Dashboard"
    ]
    
    px_coords = [1.2, 3.4, 5.6, 7.8, 10.0, 12.2, 14.4]
    p_width = 1.8
    p_height = 0.75
    top_y = 7.2
    bottom_y = 0.8

    # Draw Participant Headers & Vertical Dotted Lifelines (Top ONLY)
    for idx, p_name in enumerate(participants):
        cx = px_coords[idx]
        draw_box(ax, cx - p_width/2, top_y, p_width, p_height, p_name, bg_color='#FFFFFF', border_color=BORDER_DARK, text_color=TEXT_DARK, fontsize=9.5, fontweight='bold')
        ax.plot([cx, cx], [top_y, bottom_y], color='#94A3B8', linestyle=':', linewidth=1.8, zorder=1)

    # Chronological Sequence Messages
    messages = [
        # (f_idx, t_idx, y_val, label, color, is_self_call)
        (0, 1, 6.4, "Production Batch", '#0284C7', False),
        (1, 2, 5.6, "Detect Drift", '#0284C7', False),
        (2, 3, 4.8, "Drift Result", '#0284C7', False),
        (3, 1, 4.0, "GREEN / YELLOW: Continue Monitoring", COLOR_GREEN_BORDER, False),
        (3, 4, 3.2, "RED: Trigger Retraining", COLOR_RED_BORDER, False),
        (4, 4, 2.4, "Retrain on Recent Data", COLOR_RED_BORDER, True),
        (4, 5, 1.6, "Updated Local Model", COLOR_RED_BORDER, False),
        (5, 6, 0.9, "Fraud Prediction / Metrics", '#16A34A', False)
    ]

    for f_idx, t_idx, y_val, label, color, is_self_call in messages:
        x1 = px_coords[f_idx]
        x2 = px_coords[t_idx]

        if is_self_call:
            # Self-call loop arrow on Local Model (Participant 4)
            loop_w, loop_h = 0.6, 0.35
            ax.plot([x1, x1 + loop_w, x1 + loop_w, x1], [y_val, y_val, y_val - loop_h, y_val - loop_h], color=color, lw=1.8, zorder=2)
            draw_arrow(ax, x1 + loop_w, y_val - loop_h, x1, y_val - loop_h, color=color, width=1.8)
            ax.text(
                x1 + loop_w + 0.1, y_val - loop_h/2, label,
                ha='left', va='center',
                fontsize=9.0, fontweight='bold',
                color=color, zorder=5,
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#FFFFFF', edgecolor='none', alpha=0.95)
            )
        else:
            draw_arrow(ax, x1, y_val, x2, y_val, color=color, width=1.8)
            mid_x = (x1 + x2) / 2.0
            ax.text(
                mid_x, y_val + 0.12, label,
                ha='center', va='center',
                fontsize=9.5, fontweight='bold',
                color=color, zorder=5,
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#FFFFFF', edgecolor='none', alpha=0.95)
            )

    plt.tight_layout()
    png_path = os.path.join(OUTPUT_DIR, "03_sequence_diagram.png")
    svg_path = os.path.join(OUTPUT_DIR, "03_sequence_diagram.svg")
    plt.savefig(png_path, dpi=300, bbox_inches='tight')
    plt.savefig(svg_path, bbox_inches='tight')
    plt.close()
    print(f"Saved: {png_path} and {svg_path}")


if __name__ == "__main__":
    generate_data_flow_diagram()
    generate_control_flow_diagram()
    generate_sequence_diagram()
    print("All 3 PPT-ready diagrams successfully generated with clean academic typography!")
