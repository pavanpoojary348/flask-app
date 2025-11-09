import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix
import time

# ------------------------------
#  Spam Detector Pro (Tkinter)
# ------------------------------

root = tk.Tk()
root.title("📧 Spam Detector Pro (Tkinter)")
root.geometry("650x540")
root.config(bg="#f0f0f0")

# --- Themes ---
themes = {
    "light": {"bg": "#f0f0f0", "fg": "black", "button": "#0078d7"},
    "dark": {"bg": "#1e1e1e", "fg": "white", "button": "#3a86ff"}
}
current_theme = "light"

def apply_theme():
    theme = themes[current_theme]
    root.config(bg=theme["bg"])
    for widget in root.winfo_children():
        try:
            widget.config(bg=theme["bg"], fg=theme["fg"])
        except:
            pass
    for b in [detect_btn, clear_btn, perf_btn, save_btn, batch_btn, theme_btn]:
        b.config(bg=theme["button"], fg="white")

def toggle_theme():
    global current_theme
    current_theme = "dark" if current_theme == "light" else "light"
    apply_theme()

# --- Title ---
tk.Label(root, text="Email Spam Detector", font=("Arial", 18, "bold"), bg="#f0f0f0").pack(pady=10)

# --- Input area ---
tk.Label(root, text="Enter email text below:", font=("Arial", 12, "bold"), bg="#f0f0f0").pack()
text_box = tk.Text(root, height=8, width=70, wrap="word", font=("Arial", 10))
text_box.pack(pady=8)

result_label = tk.Label(root, text="", bg="#f0f0f0", font=("Arial", 13, "bold"))
result_label.pack(pady=10)

# --- Progress Bar (for both modes) ---
progress_frame = tk.Frame(root, bg="#f0f0f0")
progress_frame.pack(pady=10)
progress_label = tk.Label(progress_frame, text="Ready...", bg="#f0f0f0", font=("Arial", 10, "bold"))
progress_label.pack()
progress = ttk.Progressbar(progress_frame, orient="horizontal", length=400, mode="determinate")
progress.pack(pady=5)

# --- Fake Progress (animated loading for single email) ---
def fake_progress(callback, text_length):
    progress_frame.pack(pady=10)
    progress["value"] = 0
    progress["maximum"] = 100
    progress_label.config(text="Analyzing email...")

    # Adjust speed based on email length
    if text_length < 100:
        delay = 5      # fast
    elif text_length < 500:
        delay = 10     # medium
    elif text_length < 1000:
        delay = 15     # slower
    else:
        delay = 25     # longest emails

    def step(i=0):
        if i < 100:
            progress["value"] = i
            root.update_idletasks()
            root.after(delay, lambda: step(i + 5))
        else:
            progress["value"] = 100
            root.update_idletasks()
            # Give UI a tiny moment to render before running prediction
            root.after(300, lambda: finish())

    def finish():
        progress_label.config(text="✅ Analysis complete")
        callback()

    step()

# --- Prediction Function ---
def predict_spam():
    text = text_box.get("1.0", "end-1c").strip()
    if not text:
        messagebox.showwarning("⚠️ Warning", "Please enter some text first!")
        return

    def classify():
        try:
            model = joblib.load("logistic_regression_model.joblib")
            data = joblib.load("preprocessed_data_full.joblib")
            vectorizer = data["vectorizer"]

            X_input = vectorizer.transform([text])
            prediction = model.predict(X_input)[0]

            # Color progress bar based on prediction
            if prediction == 1:
                progress.configure(style="red.Horizontal.TProgressbar")
                result_label.config(text="🚨 Prediction: SPAM (1)", fg="red")
            else:
                progress.configure(style="green.Horizontal.TProgressbar")
                result_label.config(text="✅ Prediction: HAM (0)", fg="green")
        except Exception as e:
            messagebox.showerror("Error", f"Something went wrong:\n{e}")

    text_length = len(text)
    fake_progress(classify, text_length)

# --- Custom progress bar colors ---
style = ttk.Style()
style.theme_use('clam')
style.configure("green.Horizontal.TProgressbar", troughcolor='white', background='limegreen')
style.configure("red.Horizontal.TProgressbar", troughcolor='white', background='red')

# --- Clear Function ---
def clear_text():
    text_box.delete("1.0", tk.END)
    result_label.config(text="")
    progress_label.config(text="Ready...")
    progress["value"] = 0

# --- View Performance ---
def view_performance():
    try:
        data = joblib.load("preprocessed_data_full.joblib")
        X_test, y_test = data["X_test"], data["y_test"]
        model = joblib.load("logistic_regression_model.joblib")
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        cm = confusion_matrix(y_test, preds)
        msg = f"Model Accuracy: {acc*100:.2f}%\n\nConfusion Matrix:\n{cm}"
        messagebox.showinfo("📊 Model Performance", msg)
    except Exception as e:
        messagebox.showerror("Error", f"Unable to load model performance:\n{e}")

# --- Save Prediction ---
def save_result():
    text = text_box.get("1.0", "end-1c").strip()
    result = result_label.cget("text")
    if not text or not result:
        messagebox.showwarning("⚠️ Warning", "Please enter text and predict before saving!")
        return
    try:
        df = pd.DataFrame([[text, result]], columns=["Email", "Prediction"])
        save_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save Prediction Result"
        )
        if save_path:
            df.to_csv(save_path, index=False)
            messagebox.showinfo("✅ Saved", f"Result saved to:\n{save_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not save file:\n{e}")

# --- 🗂 Batch Mode with Progress Bar ---
def batch_mode():
    try:
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv")]
        )
        if not file_path:
            return

        df = pd.read_csv(file_path)
        if "text" not in df.columns:
            messagebox.showerror("Error", "The CSV must contain a column named 'text'.")
            return

        model = joblib.load("logistic_regression_model.joblib")
        data = joblib.load("preprocessed_data_full.joblib")
        vectorizer = data["vectorizer"]

        progress_label.config(text="Processing emails... Please wait.")
        total = len(df)
        progress["value"] = 0
        progress["maximum"] = total

        preds = []
        for i, text in enumerate(df["text"]):
            X_input = vectorizer.transform([text])
            pred = model.predict(X_input)[0]
            preds.append("Spam (1)" if pred == 1 else "Ham (0)")
            progress["value"] = i + 1
            progress_label.config(text=f"Processing: {i+1}/{total}")
            root.update_idletasks()
            time.sleep(0.002)  # smooth animation

        df["Prediction"] = preds
        save_path = file_path.replace(".csv", "_predicted.csv")
        df.to_csv(save_path, index=False)

        progress_label.config(text=f"✅ Completed! Results saved to: {save_path}")
        messagebox.showinfo("✅ Batch Completed", f"Predictions saved to:\n{save_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Batch processing failed:\n{e}")
    finally:
        progress["value"] = 0

# --- Buttons ---
btn_frame = tk.Frame(root, bg="#f0f0f0")
btn_frame.pack(pady=10)

detect_btn = tk.Button(btn_frame, text="Detect Spam", command=predict_spam, width=15, font=("Arial", 10, "bold"))
detect_btn.grid(row=0, column=0, padx=5)

clear_btn = tk.Button(btn_frame, text="Clear", command=clear_text, width=10, font=("Arial", 10, "bold"))
clear_btn.grid(row=0, column=1, padx=5)

perf_btn = tk.Button(btn_frame, text="📊 View Performance", command=view_performance, width=18, font=("Arial", 10, "bold"))
perf_btn.grid(row=0, column=2, padx=5)

save_btn = tk.Button(btn_frame, text="💾 Save Prediction", command=save_result, width=18, font=("Arial", 10, "bold"))
save_btn.grid(row=0, column=3, padx=5)

batch_btn = tk.Button(root, text="🗂 Batch Mode", command=batch_mode, font=("Arial", 10, "bold"), width=18)
batch_btn.pack(pady=8)

theme_btn = tk.Button(root, text="🎨 Change Theme", command=toggle_theme, font=("Arial", 10, "bold"), width=18)
theme_btn.pack(pady=8)

# --- Footer ---
tk.Label(root, text="Model: Logistic Regression | TF-IDF | Enron Dataset",
         bg="#f0f0f0", fg="gray", font=("Arial", 9)).pack(side="bottom", pady=10)

apply_theme()
root.mainloop()
