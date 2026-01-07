"""
Enhanced SoulSense App with XAI - Use this file instead of app.py
All original functionality + XAI explanations
"""
import sqlite3
import tkinter as tk
from tkinter import messagebox, Toplevel, scrolledtext
from xai_explainer import SoulSenseXAI

# DATABASE SETUP
conn = sqlite3.connect("soulsense_db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    age INTEGER,
    total_score INTEGER
)
""")
conn.commit()

# Initialize XAI
xai = SoulSenseXAI()

# QUESTIONS
questions = [
    {"text": "You can recognize your emotions as they happen.", "age_min": 12, "age_max": 25},
    {"text": "You find it easy to understand why you feel a certain way.", "age_min": 14, "age_max": 30},
    {"text": "You can control your emotions even in stressful situations.", "age_min": 15, "age_max": 35},
    {"text": "You reflect on your emotional reactions to situations.", "age_min": 13, "age_max": 28},
    {"text": "You are aware of how your emotions affect others.", "age_min": 16, "age_max": 40}
]

# USER DETAILS WINDOW
root = tk.Tk()
root.title("SoulSense - Emotional Intelligence Assessment")
root.geometry("450x350")
root.resizable(False, False)

# Set window icon (optional)
try:
    root.iconbitmap('icon.ico')
except:
    pass

# Configure colors
bg_color = "#f0f8ff"
button_color = "#4CAF50"
text_color = "#333333"

root.configure(bg=bg_color)

username = tk.StringVar()
age = tk.StringVar()

# Header
header = tk.Label(
    root,
    text="🧠 SoulSense Assessment",
    font=("Arial", 22, "bold"),
    bg=bg_color,
    fg="#2c3e50"
)
header.pack(pady=20)

# Subtitle
tk.Label(
    root,
    text="Emotional Intelligence Evaluation",
    font=("Arial", 12),
    bg=bg_color,
    fg="#7f8c8d"
).pack()

# Username field
tk.Label(
    root, 
    text="Enter your name:", 
    font=("Arial", 14, "bold"),
    bg=bg_color,
    fg=text_color
).pack(pady=(20, 5))

tk.Entry(
    root, 
    textvariable=username, 
    font=("Arial", 13), 
    width=25,
    relief=tk.GROOVE,
    bd=2
).pack(pady=5)

# Age field
tk.Label(
    root, 
    text="Enter your age:", 
    font=("Arial", 14, "bold"),
    bg=bg_color,
    fg=text_color
).pack(pady=(15, 5))

tk.Entry(
    root, 
    textvariable=age, 
    font=("Arial", 13), 
    width=25,
    relief=tk.GROOVE,
    bd=2
).pack(pady=5)

def submit_details():
    """Validate and start assessment"""
    if not username.get().strip():
        messagebox.showerror("Error", "Please enter your name")
        return
    
    if not age.get().isdigit():
        messagebox.showerror("Error", "Please enter a valid age (numbers only)")
        return
    
    age_int = int(age.get())
    if age_int < 12 or age_int > 100:
        messagebox.showerror("Error", "Age must be between 12 and 100")
        return
    
    root.destroy()
    start_quiz(username.get().strip(), age_int)

# Start button
tk.Button(
    root,
    text="🚀 Start Assessment",
    command=submit_details,
    bg=button_color,
    fg="white",
    font=("Arial", 14, "bold"),
    width=20,
    height=2,
    relief=tk.RAISED,
    bd=3,
    cursor="hand2"
).pack(pady=25)

# Footer
tk.Label(
    root,
    text="Your emotional intelligence journey starts here",
    font=("Arial", 10),
    bg=bg_color,
    fg="#7f8c8d"
).pack(side=tk.BOTTOM, pady=10)

# QUIZ WINDOW
def start_quiz(username, age):
    """Main assessment window"""
    filtered_questions = [
        q for q in questions if q["age_min"] <= age <= q["age_max"]
    ]
    
    if not filtered_questions:
        messagebox.showinfo("No Questions", "No questions available for your age group.")
        return
    
    quiz = tk.Tk()
    quiz.title(f"SoulSense Assessment - {username}")
    quiz.geometry("800x600")
    quiz.configure(bg=bg_color)
    
    # Progress tracking
    score = 0
    current_q = 0
    var = tk.IntVar()
    
    # Question counter
    counter_label = tk.Label(
        quiz,
        text=f"Question 1 of {len(filtered_questions)}",
        font=("Arial", 12, "bold"),
        bg=bg_color,
        fg="#3498db"
    )
    counter_label.pack(pady=10)
    
    # Question display
    question_frame = tk.Frame(quiz, bg=bg_color)
    question_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)
    
    question_label = tk.Label(
        question_frame,
        text="",
        wraplength=700,
        font=("Arial", 16, "bold"),
        bg=bg_color,
        fg="#2c3e50",
        justify="center"
    )
    question_label.pack(pady=20)
    
    # Response options
    options_frame = tk.Frame(quiz, bg=bg_color)
    options_frame.pack(pady=10)
    
    options = [
        ("😔 Strongly Disagree", 1),
        ("🙁 Disagree", 2),
        ("😐 Neutral", 3),
        ("🙂 Agree", 4),
        ("😊 Strongly Agree", 5)
    ]
    
    for text, val in options:
        rb = tk.Radiobutton(
            options_frame,
            text=text,
            variable=var,
            value=val,
            font=("Arial", 13),
            bg=bg_color,
            fg=text_color,
            selectcolor="#e3f2fd",
            activebackground=bg_color,
            indicatoron=True,
            width=25,
            anchor="w"
        )
        rb.pack(pady=3, padx=50, anchor="w")
    
    def load_question():
        """Load current question"""
        question_label.config(text=filtered_questions[current_q]["text"])
        counter_label.config(text=f"Question {current_q + 1} of {len(filtered_questions)}")
    
    def next_question():
        """Handle next question or completion"""
        nonlocal current_q, score
        
        if var.get() == 0:
            messagebox.showwarning("Warning", "Please select an option before continuing")
            return
        
        score += var.get()
        var.set(0)
        current_q += 1
        
        if current_q < len(filtered_questions):
            load_question()
        else:
            # Save score to database
            cursor.execute(
                "INSERT INTO scores (username, age, total_score) VALUES (?, ?, ?)",
                (username, age, score)
            )
            conn.commit()
            
            # Get user ID
            user_id = cursor.lastrowid
            
            # Generate XAI explanation
            explanation = xai.analyze_score(score, username, age)
            
            # Save explanation
            xai.save_explanation(user_id, score, explanation)
            
            # Show results with XAI
            show_results(username, score, explanation)
            quiz.destroy()
    
    def show_results(username, score, explanation):
        """Display results with XAI explanation"""
        results_window = Toplevel()
        results_window.title("Assessment Results")
        results_window.geometry("900x700")
        results_window.configure(bg=bg_color)
        
        # Header
        tk.Label(
            results_window,
            text="🎯 Assessment Complete!",
            font=("Arial", 24, "bold"),
            bg=bg_color,
            fg="#2c3e50"
        ).pack(pady=20)
        
        # Score display
        score_frame = tk.Frame(results_window, bg="#e8f5e9", relief=tk.RAISED, bd=2)
        score_frame.pack(pady=10, padx=50, fill=tk.X)
        
        tk.Label(
            score_frame,
            text=f"👤 User: {username}",
            font=("Arial", 14),
            bg="#e8f5e9"
        ).pack(pady=5)
        
        tk.Label(
            score_frame,
            text=f"📊 Total Score: {score}/25",
            font=("Arial", 18, "bold"),
            bg="#e8f5e9",
            fg="#27ae60"
        ).pack(pady=10)
        
        # Score interpretation
        if score <= 10:
            interpretation = "🔴 Areas for Growth"
            color = "#e74c3c"
        elif score <= 15:
            interpretation = "🟡 Moderate Awareness"
            color = "#f39c12"
        else:
            interpretation = "🟢 Strong Emotional Intelligence"
            color = "#27ae60"
        
        tk.Label(
            results_window,
            text=interpretation,
            font=("Arial", 16, "bold"),
            bg=bg_color,
            fg=color
        ).pack(pady=10)
        
        # XAI Explanation Section
        tk.Label(
            results_window,
            text="📋 Detailed Analysis",
            font=("Arial", 18, "bold"),
            bg=bg_color,
            fg="#2c3e50"
        ).pack(pady=(20, 10))
        
        # Scrolled text for explanation
        explanation_text = scrolledtext.ScrolledText(
            results_window,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=("Arial", 11),
            bg="#f8f9fa",
            relief=tk.GROOVE,
            bd=2
        )
        explanation_text.pack(pady=10, padx=50)
        explanation_text.insert(tk.END, explanation)
        explanation_text.config(state=tk.DISABLED)  # Make read-only
        
        # Buttons
        button_frame = tk.Frame(results_window, bg=bg_color)
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="💾 Save Report",
            command=lambda: save_report(username, score, explanation),
            bg="#3498db",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15,
            relief=tk.RAISED
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            button_frame,
            text="🔄 Take Again",
            command=lambda: [results_window.destroy(), start_quiz(username, age)],
            bg="#9b59b6",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15,
            relief=tk.RAISED
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            button_frame,
            text="❌ Close",
            command=lambda: [results_window.destroy(), close_app()],
            bg="#e74c3c",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15,
            relief=tk.RAISED
        ).pack(side=tk.LEFT, padx=10)
    
    def save_report(username, score, explanation):
        """Save report to text file"""
        filename = f"soulsense_report_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(explanation)
        messagebox.showinfo("Saved", f"Report saved as {filename}")
    
    def close_app():
        """Close application"""
        conn.close()
        xai.close()
        root.quit()
    
    # Next button
    button_frame = tk.Frame(quiz, bg=bg_color)
    button_frame.pack(pady=20)
    
    tk.Button(
        button_frame,
        text="➡️ Next Question" if current_q < len(filtered_questions) - 1 else "🏁 Finish",
        command=next_question,
        bg=button_color,
        fg="white",
        font=("Arial", 14, "bold"),
        width=20,
        height=2,
        relief=tk.RAISED,
        bd=3,
        cursor="hand2"
    ).pack()
    
    # Load first question
    load_question()
    quiz.mainloop()


# Import datetime at the top (add this line)
from datetime import datetime

# Start the app
if __name__ == "__main__":
    root.mainloop()
