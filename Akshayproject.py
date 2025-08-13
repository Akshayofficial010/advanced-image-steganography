import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from stegano import lsb
import smtplib
from email.message import EmailMessage
import os


class AnimatedGIF(tk.Label):
    """A Label that displays an animated GIF as background."""
    def __init__(self, master, gif_path, **kwargs):
        super().__init__(master, **kwargs)
        self.gif_path = gif_path
        self.frames = []
        try:
            self.load_frames()
            self.idx = 0
            self.delay = int(self.image.info.get('duration', 100))
            self.animate_gif()
        except Exception as e:
            print("AnimatedGIF load failed:", e)

    def load_frames(self):
        self.image = Image.open(self.gif_path)
        self.frames.clear()
        try:
            i = 0
            while True:
                self.image.seek(i)
                w = max(1, self.master.winfo_width())
                h = max(1, self.master.winfo_height())
                frame = ImageTk.PhotoImage(self.image.copy().resize((w, h), Image.LANCZOS))
                self.frames.append(frame)
                i += 1
        except EOFError:
            pass

    def animate_gif(self):
        if self.frames:
            self.config(image=self.frames[self.idx])
            self.idx = (self.idx + 1) % len(self.frames)
            self.after(self.delay, self.animate_gif)


def send_email(sender, passwd, receiver, attachment_path):
    msg = EmailMessage()
    msg['Subject'] = 'Stego Image'
    msg['From'] = sender
    msg['To'] = receiver
    msg.set_content('Find the stego image attached with the hidden message.')

    with open(attachment_path, 'rb') as f:
        img_data = f.read()
        msg.add_attachment(img_data, maintype='image', subtype='png', filename=os.path.basename(attachment_path))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, passwd)
        server.send_message(msg)


class StegoApp(tk.Tk):
    def __init__(self, gif_path, fg_image_path):
        super().__init__()
        self.title("Image Steganography (Any Input → PNG Output)")
        self.geometry('900x650')
        self.resizable(False, False)

        self.fg_image_path = fg_image_path
        self.update_idletasks()

        # Background GIF
        self.bg_label = AnimatedGIF(self, gif_path)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Foreground frame (center)
        self.fg_frame = tk.Frame(self, bd=10, relief='ridge')
        self.fg_frame.place(relx=0.5, rely=0.5, anchor='center', width=620, height=560)

        # Foreground image filling fg_frame
        try:
            self.fg_image = Image.open(fg_image_path)
            self.fg_image = self.fg_image.resize((620, 560), Image.LANCZOS)
            self.fg_image_tk = ImageTk.PhotoImage(self.fg_image)
            self.fg_bg_label = tk.Label(self.fg_frame, image=self.fg_image_tk)
            self.fg_bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print("Failed to load foreground image:", e)
            self.fg_bg_label = tk.Label(self.fg_frame, bg="#ffffff")
            self.fg_bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Button frame on top of foreground image
        self.button_frame = tk.Frame(self.fg_frame, bg='', bd=0)
        self.button_frame.place(relx=0.5, y=60, anchor='n')

        # stacking order: ensure fg_frame above background, buttons above fg image
        self.fg_frame.lift(self.bg_label)
        self.button_frame.lift(self.fg_bg_label)

        self.create_widgets()
        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        if event.widget == self:
            try:
                self.bg_label.frames.clear()
                self.bg_label.load_frames()
            except Exception:
                pass

    def create_widgets(self):
        tk.Label(self.button_frame, text="Image Steganography (Any Image → PNG)",
                 font=('Arial', 18, 'bold'), bg='white', fg='black').pack(pady=10)

        tk.Button(self.button_frame, text="Project Info", width=32, font=('Arial', 14),
                  command=self.show_info).pack(pady=8)
        tk.Button(self.button_frame, text="Hide Text & Send Email", width=32, font=('Arial', 14),
                  command=self.hide_text_window).pack(pady=8)
        tk.Button(self.button_frame, text="Extract Text from Image", width=32, font=('Arial', 14),
                  command=self.extract_text_window).pack(pady=8)
        tk.Button(self.button_frame, text="Guide", width=32, font=('Arial', 14),
                  command=self.guide_info).pack(pady=8)

    def show_info(self):
        # The rest of your scrollable Project Info window code unchanged...

        info_win = tk.Toplevel(self)
        info_win.title("Project Information")
        info_win.geometry("700x520")
        info_win.resizable(False, False)

        canvas = tk.Canvas(info_win, borderwidth=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(info_win, orient="vertical", command=canvas.yview)
        scroll_container = tk.Frame(canvas)
        scroll_container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(scroll_container, text="Project Information", font=("Arial", 18, "bold")).pack(pady=10, anchor="w")

        desc_text = (
            "This project was developed by the following team as part of a Cyber Security Internship. "
            "It demonstrates hiding text inside images using the LSB technique and ensures extraction "
            "reliability by outputting the stego image as PNG when sending."
        )
        tk.Label(scroll_container, text=desc_text, wraplength=660, justify="left", font=("Arial", 11)).pack(pady=6, anchor="w")

        tk.Label(scroll_container, text="Team Members:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(6, 0))
        team_frame = tk.Frame(scroll_container)
        team_frame.pack(fill="x", padx=12, pady=(0, 6))
        members = [
            "M Akshay Kumar",
            "Gnaneshwar",
            "Manojpal",
            "Shoumik"
        ]
        for m in members:
            tk.Label(team_frame, text=f"•  {m}", font=("Arial", 11), anchor="w").pack(anchor="w")

        def create_table(parent, headings, rows, col_weights=None, total_inner_width=660):
            cols = len(headings)
            if col_weights is None:
                col_weights = [1] * cols
            sum_w = max(1, sum(col_weights))
            col_widths = [max(60, int(total_inner_width * (w / sum_w))) for w in col_weights]

            table_frame = tk.Frame(parent, bd=1, relief="solid")
            table_frame.pack(pady=8, fill="x", padx=10)

            for col, heading in enumerate(headings):
                lbl = tk.Label(table_frame, text=heading, font=("Arial", 11, "bold"),
                              borderwidth=1, relief="solid", anchor="w", bg="#f0f0f0",
                              padx=6, pady=6, wraplength=col_widths[col]-12)
                lbl.grid(row=0, column=col, sticky="nsew")
                table_frame.grid_columnconfigure(col, weight=col_weights[col])

            for r, row in enumerate(rows, start=1):
                row_items = list(row) + [''] * (cols - len(row))
                for c, value in enumerate(row_items[:cols]):
                    lbl = tk.Label(table_frame, text=value, font=("Arial", 11),
                                   borderwidth=1, relief="solid", anchor="w",
                                   padx=6, pady=6, wraplength=col_widths[c]-12, justify="left")
                    lbl.grid(row=r, column=c, sticky="nsew")
            return table_frame

        tk.Label(scroll_container, text="Project Details", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
        create_table(scroll_container,
            ["Field", "Value"],
            [
                ["Project Name", "Image Steganography using LSB"],
                ["Project Description", "Hiding Message with Encryption in Image using LSB algorithm; output stego image as PNG for safe extraction."],
                ["Project Start Date", "14-July-2025"],
                ["Project End Date", "14-August-2025"],
                ["Project Status", "Completed"]
            ],
            col_weights=[1, 3]
        )

        tk.Label(scroll_container, text="Developer Details (Organization)", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        create_table(scroll_container,
            ["Organization", "Employee ID", "Contact Email"],
            [["Supraja Technologies", "ST#IS#7547", "akshaykumarmuthyam@gmail.com"],
            ["Supraja Technologies", "ST#IS#7552", "gnaneshwar010@gmail.com"],
            ["Supraja Technologies", "ST#IS#7550", "contact@suprajatechnologies.com"],
            ["Supraja Technologies", "ST#IS#7539", "shoumikreddy098@gmail.com"]
            ],
            col_weights=[3, 1, 3]
        )

        tk.Label(scroll_container, text="Company Details", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        create_table(scroll_container,
            ["Company Field", "Value"],
            [
                ["Company Name", "Supraja Technologies"],
                ["Company Email", "contact@suprajatechnologies.com"],
                ["Company Address", "Supraja Technologies Pvt. Ltd. (use actual address if needed)"]
            ],
            col_weights=[1, 3]
        )

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def hide_text_window(self):
        """Popup to hide text and send stego PNG by email (accepts many input formats)."""
        window = tk.Toplevel(self)
        window.title("Hide Text & Send Email")
        window.geometry('560x370')
        window.resizable(False, False)

        try:
            bg_img = Image.open(self.fg_image_path).resize((560, 370), Image.LANCZOS)
            self.hide_bg_tk = ImageTk.PhotoImage(bg_img)
            bg_label = tk.Label(window, image=self.hide_bg_tk)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception:
            bg_label = tk.Label(window, bg="#ffffff")
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        form_frame = tk.Frame(window, bg='', bd=0)
        form_frame.place(relx=0.5, rely=0.05, anchor='n')
        form_frame.lift(bg_label)

        labels = [
            "Select Image:",
            "Secret Message:",
            "Sender Email (Gmail):",
            "Sender Email Password:",
            "Receiver Email:"
        ]
        entries = {}

        for i, label in enumerate(labels):
            tk.Label(form_frame, text=label, font=('Arial', 13), bg='white').grid(row=i, column=0, sticky='w', padx=12, pady=8)
            entry = tk.Entry(form_frame, font=('Arial', 13), show='*' if "Password" in label else '')
            entry.grid(row=i, column=1, padx=12, pady=8, sticky='ew')
            if i < len(labels) - 1:
                entry.bind('<Return>', lambda e, en=entries, idx=i: list(en.values())[idx + 1].focus_set())
            entries[label] = entry

        tk.Button(form_frame, text="Browse",
                  command=lambda: self.browse_image(entries["Select Image:"])).grid(row=0, column=2, padx=6)
        form_frame.grid_columnconfigure(1, weight=1)

        def hide_and_send():
            img_path = entries["Select Image:"].get().strip()
            secret_msg = entries["Secret Message:"].get()
            sender_email = entries["Sender Email (Gmail):"].get().strip()
            sender_passwd = entries["Sender Email Password:"].get()
            receiver_email = entries["Receiver Email:"].get().strip()

            if not all([img_path, secret_msg, sender_email, sender_passwd, receiver_email]):
                messagebox.showerror("Error", "All fields are required.")
                return

            try:
                stego_img = lsb.hide(img_path, secret_msg)
                stego_img_path = "stego_image.png"
                stego_img.save(stego_img_path, format="PNG")
                send_email(sender_email, sender_passwd, receiver_email, stego_img_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to hide/send image: {e}")
                return

            messagebox.showinfo("Success", f"Stego PNG image sent to {receiver_email}")
            window.destroy()

        tk.Button(window, text="Hide & Send", bg='red', fg='white', font=('Arial', 14),
                  command=hide_and_send).place(relx=0.5, rely=0.88, anchor='center')

    def browse_image(self, entry_widget):
        file_path = filedialog.askopenfilename(filetypes=[
            ("Image files", ".png;.jpg;.jpeg;.bmp;.gif;.tiff;*.webp"),
            ("All files", ".")
        ])
        if file_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, file_path)

    def extract_text_window(self):
        file_path = filedialog.askopenfilename(
            title="Select PNG image to extract from",
            filetypes=[("PNG images", "*.png")]
        )
        if not file_path:
            return
        try:
            hidden_msg = lsb.reveal(file_path)
            if hidden_msg:
                messagebox.showinfo("Hidden Message Extracted", hidden_msg)
            else:
                messagebox.showinfo("Result", "No hidden message found in the image.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract message: {e}")

    def guide_info(self):
        guide_win = tk.Toplevel(self)
        guide_win.title("Application Guide")
        guide_win.geometry("700x520")
        guide_win.resizable(False, False)

        canvas = tk.Canvas(guide_win, borderwidth=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(guide_win, orient="vertical", command=canvas.yview)
        scroll_container = tk.Frame(canvas)
        scroll_container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(scroll_container, text="User Guide", font=("Arial", 18, "bold")).pack(pady=10, anchor="w")

        intro_text = (
            "This guide explains how to use the Image Steganography application.\n"
            "Follow these steps to hide messages in images, send them securely, "
            "and extract hidden messages."
        )
        tk.Label(scroll_container, text=intro_text, wraplength=660, justify="left", font=("Arial", 11)).pack(pady=6, anchor="w")

        steps = [
            ("1. Launch the Application",
             "Open the program. You will see three main options:\n"
             "• Project Info\n"
             "• Hide Text & Send Email\n"
             "• Extract Text from Image\n"),
            ("2. Hide Text & Send Email",
             "Click 'Hide Text & Send Email'.\n"
             "a) Browse and select ANY image (JPG, PNG, BMP, etc.).\n"
             "b) Type your secret message.\n"
             "c) Enter sender Gmail address and password.\n"
             "d) Enter recipient email address.\n"
             "e) Click 'Hide & Send'.\n\n"
             "The image will be processed and saved as PNG before being sent via email."),
            ("3. Extract Text from Image",
             "Click 'Extract Text from Image'.\n"
             "a) Browse and select the PNG image with the hidden message.\n"
             "b) The hidden text will be revealed if found.\n\n"
             "Note: Extraction works only from PNG files created by this application."),
            ("4. Security Tip",
             "Avoid sharing the email password with others.\n"
             "Always use a separate account for testing.\n"
             "The message is hidden using LSB steganography for security.")
        ]

        for title, desc in steps:
            tk.Label(scroll_container, text=title, font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(8, 0))
            tk.Label(scroll_container, text=desc, wraplength=660, justify="left", font=("Arial", 11)).pack(anchor="w", padx=20)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)


if __name__ == "__main__":
    # <-- update these paths to your local files if needed -->
    gif_path = r"C:\Users\aksha\OneDrive\Desktop\New folder\speed blur GIF by Chris Gannon.gif"
    fg_image_path = r"C:\Users\aksha\OneDrive\Desktop\New folder\hello.jpg"
    app = StegoApp(gif_path, fg_image_path)
    app.mainloop()