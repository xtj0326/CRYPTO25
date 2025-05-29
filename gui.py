import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import numpy as np
from PIL import Image, ImageTk
import os
import io
from tkinterdnd2 import DND_FILES, TkinterDnD
from chaotic_permutation import logistic_map, chebyshev_map, tent_map, generate_permutation

def encrypt_text(message, disorganizedtable):
    c_list = [''] * len(message)
    for i in range(len(message)):
        c_list[disorganizedtable[i]] = message[i]
    return ''.join(c_list)

def decrypt_text(ciphertext, disorganizedtable):
    dedisorganizedtable = [0] * len(disorganizedtable)
    for i in range(len(disorganizedtable)):
        dedisorganizedtable[disorganizedtable[i]] = i
    
    m_list = [''] * len(ciphertext)
    
    for i in range(len(ciphertext)):
        m_list[dedisorganizedtable[i]] = ciphertext[i]
    
    return ''.join(m_list)

def encrypt_img(image_array, permutation_x, permutation_y):
    height, width = image_array.shape[:2]
    encrypted_image = np.zeros_like(image_array)
    
    for i in range(height):
        for j in range(width):
            new_i = permutation_y[i]
            new_j = permutation_x[j]
            encrypted_image[new_i, new_j] = image_array[i, j]
    
    return encrypted_image

def decrypt_img(encrypted_image, permutation_x, permutation_y):
    height, width = encrypted_image.shape[:2]
    decrypted_image = np.zeros_like(encrypted_image)
    
    inverse_perm_x = [0] * len(permutation_x)
    for i, pos in enumerate(permutation_x):
        inverse_perm_x[pos] = i
    
    inverse_perm_y = [0] * len(permutation_y)
    for i, pos in enumerate(permutation_y):
        inverse_perm_y[pos] = i
    
    for i in range(height):
        for j in range(width):
            orig_i = inverse_perm_y[i]
            orig_j = inverse_perm_x[j]
            decrypted_image[orig_i, orig_j] = encrypted_image[i, j]
    
    return decrypted_image

def encrypt_pixels(image_array, chaotic_map, seed, **map_params):
    height, width = image_array.shape[:2]
    channels = 1 if len(image_array.shape) == 2 else image_array.shape[2]
    
    encrypted_image = np.copy(image_array)
    
    x = seed
    for _ in range(1000):
        x = chaotic_map(x, **map_params)
    
    for i in range(height):
        for j in range(width):
            for c in range(channels):
                x = chaotic_map(x, **map_params)
                
                if chaotic_map == chebyshev_map:
                    chaotic_value = int(((x + 1) / 2) * 255)
                else:
                    chaotic_value = int(x * 255)
                
                if len(image_array.shape) == 2:
                    encrypted_image[i, j] = encrypted_image[i, j] ^ chaotic_value
                else:
                    encrypted_image[i, j, c] = encrypted_image[i, j, c] ^ chaotic_value
    
    return encrypted_image

def decrypt_pixels(encrypted_image, chaotic_map, seed, **map_params):
    return encrypt_pixels(encrypted_image, chaotic_map, seed, **map_params)

class ChaoticCipherApp:
    def __init__(self, root):
        self.root = TkinterDnD.Tk() if not isinstance(root, tk.Tk) else root
        self.root.title("混沌置乱加密/解密")
        self.root.geometry("1100x800")
        
        self.current_image = None
        self.mode = tk.StringVar(value="text")
        
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        ttk.Label(control_frame, text="选择加密模式:").pack(anchor=tk.W, pady=5)
        modes = [
            ("文本加密", "text"),
            ("图片加密", "image")
        ]
        for text, value in modes:
            ttk.Radiobutton(control_frame, text=text, value=value, 
                           variable=self.mode, command=self.change_mode).pack(anchor=tk.W)
        
        self.text_param_frame = ttk.LabelFrame(control_frame, text="文本加密参数", padding="5")
        self.text_param_frame.pack(fill=tk.X, pady=10, padx=5)
        
        ttk.Label(self.text_param_frame, text="选择混沌映射:").pack(anchor=tk.W, pady=5)
        self.text_map_var = tk.StringVar(value="logistic")
        maps = [
            ("Logistic映射", "logistic"),
            ("Chebyshev映射", "chebyshev"),
            ("帐篷映射", "tent")
        ]
        for text, value in maps:
            ttk.Radiobutton(self.text_param_frame, text=text, value=value, 
                          variable=self.text_map_var).pack(anchor=tk.W)
        
        seed_frame = ttk.Frame(self.text_param_frame)
        seed_frame.pack(fill=tk.X, pady=5)
        ttk.Label(seed_frame, text="初始值:").pack(side=tk.LEFT)
        self.text_seed_var = tk.StringVar(value="0.1")
        ttk.Entry(seed_frame, textvariable=self.text_seed_var, width=10).pack(side=tk.LEFT, padx=5)
        
        self.image_param_frame = ttk.LabelFrame(control_frame, text="图片混合加密参数", padding="5")
        self.image_param_frame.pack(fill=tk.X, pady=10, padx=5)
        self.image_param_frame.pack_forget()
        
        ttk.Label(self.image_param_frame, text="位置加密参数 - 行").pack(anchor=tk.W, pady=(10, 5))
        
        ttk.Label(self.image_param_frame, text="选择混沌映射:").pack(anchor=tk.W, pady=5)
        self.row_map_var = tk.StringVar(value="logistic")
        for text, value in maps:
            ttk.Radiobutton(self.image_param_frame, text=text, value=value, 
                          variable=self.row_map_var).pack(anchor=tk.W)
        
        row_seed_frame = ttk.Frame(self.image_param_frame)
        row_seed_frame.pack(fill=tk.X, pady=5)
        ttk.Label(row_seed_frame, text="初始值:").pack(side=tk.LEFT)
        self.row_seed_var = tk.StringVar(value="0.1")
        ttk.Label(row_seed_frame, text="(设为0禁用行置乱)").pack(side=tk.RIGHT)
        ttk.Entry(row_seed_frame, textvariable=self.row_seed_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.image_param_frame, text="位置加密参数 - 列").pack(anchor=tk.W, pady=(10, 5))
        
        ttk.Label(self.image_param_frame, text="选择混沌映射:").pack(anchor=tk.W, pady=5)
        self.col_map_var = tk.StringVar(value="logistic")
        for text, value in maps:
            ttk.Radiobutton(self.image_param_frame, text=text, value=value, 
                          variable=self.col_map_var).pack(anchor=tk.W)
        
        col_seed_frame = ttk.Frame(self.image_param_frame)
        col_seed_frame.pack(fill=tk.X, pady=5)
        ttk.Label(col_seed_frame, text="初始值:").pack(side=tk.LEFT)
        self.col_seed_var = tk.StringVar(value="0.2")
        ttk.Label(col_seed_frame, text="(设为0禁用列置乱)").pack(side=tk.RIGHT)
        ttk.Entry(col_seed_frame, textvariable=self.col_seed_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.image_param_frame, text="像素值加密参数").pack(anchor=tk.W, pady=(10, 5))
        
        ttk.Label(self.image_param_frame, text="选择混沌映射:").pack(anchor=tk.W, pady=5)
        self.pixel_map_var = tk.StringVar(value="logistic")
        for text, value in maps:
            ttk.Radiobutton(self.image_param_frame, text=text, value=value, 
                          variable=self.pixel_map_var).pack(anchor=tk.W)
        
        pixel_seed_frame = ttk.Frame(self.image_param_frame)
        pixel_seed_frame.pack(fill=tk.X, pady=5)
        ttk.Label(pixel_seed_frame, text="初始值:").pack(side=tk.LEFT)
        self.pixel_seed_var = tk.StringVar(value="0.3")
        ttk.Label(pixel_seed_frame, text="(设为0禁用像素值加密)").pack(side=tk.RIGHT)
        ttk.Entry(pixel_seed_frame, textvariable=self.pixel_seed_var, width=10).pack(side=tk.LEFT, padx=5)
        
        self.text_button_frame = ttk.Frame(control_frame)
        self.text_button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(self.text_button_frame, text="加密", command=self.encrypt).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.text_button_frame, text="解密", command=self.decrypt).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.text_button_frame, text="清除", command=self.clear).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.text_button_frame, text="打开文件", command=self.open_file).pack(side=tk.LEFT, padx=5)
        
        self.image_button_frame = ttk.Frame(control_frame)
        self.image_button_frame.pack(fill=tk.X, pady=10)
        self.image_button_frame.pack_forget()
        
        ttk.Button(self.image_button_frame, text="选择图片", command=self.open_img).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.image_button_frame, text="加密", command=self.encrypt_img).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.image_button_frame, text="解密", command=self.decrypt_img).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.image_button_frame, text="清除", command=self.clear_img).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.image_button_frame, text="保存", command=self.save_img).pack(side=tk.LEFT, padx=5)
        
        self.status_var = tk.StringVar(value="准备就绪")
        status_label = ttk.Label(control_frame, textvariable=self.status_var, wraplength=200)
        status_label.pack(fill=tk.X, pady=10)
        
        self.right_frame = ttk.Frame(main_frame)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.text_frame = ttk.Frame(self.right_frame)
        self.text_frame.pack(fill=tk.BOTH, expand=True)
        
        input_frame = ttk.LabelFrame(self.text_frame, text="输入文本", padding="5")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.input_text = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=15)
        self.input_text.pack(fill=tk.BOTH, expand=True)
        self.input_text.insert("1.0", "输入文本或拖拽.txt文件")
        self.input_text.bind("<FocusIn>", lambda e: self.input_text.delete("1.0", tk.END) if self.input_text.get("1.0", tk.END).strip() == "输入文本或拖拽.txt文件" else None)
        
        self.input_text.drop_target_register(DND_FILES)
        self.input_text.dnd_bind('<<Drop>>', self.on_text_drop)
        
        output_frame = ttk.LabelFrame(self.text_frame, text="输出文本", padding="5")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=15)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        self.image_frame = ttk.Frame(self.right_frame)
        self.image_frame.pack(fill=tk.BOTH, expand=True)
        self.image_frame.pack_forget()
        
        original_frame = ttk.LabelFrame(self.image_frame, text="原始图片", padding="5")
        original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.original_image_label = ttk.Label(original_frame, text="选择图片或拖拽图片")
        self.original_image_label.pack(fill=tk.BOTH, expand=True)
        
        self.original_image_label.drop_target_register(DND_FILES)
        self.original_image_label.dnd_bind('<<Drop>>', self.on_img_drop)
        
        processed_frame = ttk.LabelFrame(self.image_frame, text="处理后图片", padding="5")
        processed_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.processed_image_label = ttk.Label(processed_frame)
        self.processed_image_label.pack(fill=tk.BOTH, expand=True)
    
    def change_mode(self):
        mode = self.mode.get()
        if mode == "text":
            self.text_frame.pack(fill=tk.BOTH, expand=True)
            self.image_frame.pack_forget()
            self.text_button_frame.pack(fill=tk.X, pady=10)
            self.image_button_frame.pack_forget()
            self.text_param_frame.pack(fill=tk.X, pady=10, padx=5)
            self.image_param_frame.pack_forget()
        else:
            self.text_frame.pack_forget()
            self.image_frame.pack(fill=tk.BOTH, expand=True)
            self.text_button_frame.pack_forget()
            self.image_button_frame.pack(fill=tk.X, pady=10)
            self.text_param_frame.pack_forget()
            self.image_param_frame.pack(fill=tk.X, pady=10, padx=5)
            
            self.row_map_var.trace_add("write", lambda *args: self.update_img_params())
            self.col_map_var.trace_add("write", lambda *args: self.update_img_params())
            self.pixel_map_var.trace_add("write", lambda *args: self.update_img_params())
    
    def update_img_params(self):
        mode = self.mode.get()
        
        self.image_param_frame.pack_forget()
        
        if mode == "image":
            self.image_param_frame.pack(fill=tk.X, pady=10, padx=5)
        
        if mode == "text":
            self.status_var.set("已选择文本加密模式")
        elif mode == "image":
            self.status_var.set("已选择图片加密模式")
    
    def get_text(self, text_widget):
        content = text_widget.get("1.0", tk.END)
        if content.endswith('\n'):
            content = content[:-1]
        return content
    
    def get_map(self, map_type):
        if map_type == "logistic":
            return logistic_map, {"mu": 3.99}
        elif map_type == "chebyshev":
            return chebyshev_map, {"n": 3}
        else:
            return tent_map, {"mu": 1.99}
    
    def get_perm_text(self, size):
        map_type = self.text_map_var.get()
        seed = float(self.text_seed_var.get())
        
        chaotic_map, params = self.get_map(map_type)
        return generate_permutation(chaotic_map, seed, size, **params)
    
    def get_perm_img(self, size, dimension="row"):
        if dimension == "row":
            map_type = self.row_map_var.get()
            seed_str = self.row_seed_var.get()
        else:
            map_type = self.col_map_var.get()
            seed_str = self.col_seed_var.get()
        
        try:
            seed = float(seed_str)
            if seed == 0:
                return list(range(size))
        except ValueError:
            messagebox.showwarning("警告", f"无效的种子值: {seed_str}")
            return list(range(size))
        
        chaotic_map, params = self.get_map(map_type)
        return generate_permutation(chaotic_map, seed, size, **params)
    
    def encrypt(self):
        try:
            text = self.get_text(self.input_text)
            if not text or text == "输入文本或拖拽.txt文件":
                messagebox.showwarning("警告", "请输入要加密的文本")
                return
            permutation = self.get_perm_text(len(text))
            encrypted = encrypt_text(text, permutation)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", encrypted)
            self.status_var.set(f"加密完成，使用{self.text_map_var.get()}映射")
        except Exception as e:
            messagebox.showerror("错误", f"加密过程中出现错误: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def decrypt(self):
        try:
            text = self.get_text(self.input_text)
            if not text or text == "输入文本或拖拽.txt文件":
                messagebox.showwarning("警告", "请输入要解密的文本")
                return
            
            permutation = self.get_perm_text(len(text))
            
            decrypted = decrypt_text(text, permutation)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", decrypted)
            self.status_var.set("解密完成")
        except Exception as e:
            messagebox.showerror("错误", f"解密过程中出现错误: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def clear(self):
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", "输入文本或拖拽.txt文件")
        self.output_text.delete("1.0", tk.END)
        self.status_var.set("准备就绪")
    
    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="选择文本文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file_path:
            self.load_text(file_path)
    
    def on_text_drop(self, event):
        file_path = event.data
        file_path = file_path.strip('{}')
        if file_path.startswith('"') and file_path.endswith('"'):
            file_path = file_path[1:-1]
        
        if file_path.lower().endswith('.txt') or os.path.isfile(file_path):
            self.load_text(file_path)
        else:
            messagebox.showwarning("警告", "请选择有效的文本文件")
    
    def load_text(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", content)
            self.status_var.set(f"已加载文件: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("错误", f"加载文件时出错: {str(e)}")
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert("1.0", content)
                self.status_var.set(f"已加载文件: {os.path.basename(file_path)}（GBK编码）")
            except Exception as e2:
                messagebox.showerror("错误", f"尝试使用GBK编码读取也失败: {str(e2)}")
                import traceback
                traceback.print_exc()
    
    def open_img(self):
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图像文件", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path:
            self.load_img(file_path)
    
    def on_img_drop(self, event):
        file_path = event.data
        file_path = file_path.strip('{}')
        if file_path.startswith('"') and file_path.endswith('"'):
            file_path = file_path[1:-1]
        
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            self.load_img(file_path)
        else:
            messagebox.showwarning("警告", "请选择有效的图片文件")
    
    def load_img(self, file_path):
        try:
            image = Image.open(file_path)
            
            max_size = (400, 400)
            image.thumbnail(max_size, Image.LANCZOS)
            
            self.current_image = np.array(image)
            
            self.show_img(self.original_image_label, image)
            
            self.processed_image_label.config(image='')
            
            self.status_var.set(f"已加载图片: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("错误", f"加载图片时出错: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def show_img(self, label, image):
        photo = ImageTk.PhotoImage(image)
        label.config(image=photo)
        label.image = photo
    
    def encrypt_img(self):
        try:
            if self.current_image is None:
                messagebox.showwarning("警告", "请先加载图片")
                return
            
            processed_image = np.copy(self.current_image)
            
            height, width = processed_image.shape[:2]
            encryption_steps = []
            
            row_seed = float(self.row_seed_var.get())
            col_seed = float(self.col_seed_var.get())
            
            if row_seed != 0 or col_seed != 0:
                perm_x = self.get_perm_img(width, "column")
                perm_y = self.get_perm_img(height, "row")
                
                if perm_x != list(range(width)) or perm_y != list(range(height)):
                    processed_image = encrypt_img(processed_image, perm_x, perm_y)
                    
                    if row_seed != 0 and col_seed != 0:
                        encryption_steps.append(f"位置加密（行列均已置乱）")
                    elif row_seed != 0:
                        encryption_steps.append(f"位置加密（仅行置乱）")
                    else:
                        encryption_steps.append(f"位置加密（仅列置乱）")
            
            pixel_seed_str = self.pixel_seed_var.get()
            try:
                pixel_seed = float(pixel_seed_str)
                if pixel_seed != 0:
                    pixel_map_type = self.pixel_map_var.get()
                    
                    chaotic_map, params = self.get_map(pixel_map_type)
                    
                    processed_image = encrypt_pixels(processed_image, chaotic_map, pixel_seed, **params)
                    encryption_steps.append(f"像素值加密（{pixel_map_type}映射）")
            except ValueError:
                messagebox.showwarning("警告", f"无效的像素值种子: {pixel_seed_str}")
            
            if not encryption_steps:
                messagebox.showinfo("提示", "未执行任何加密操作，请设置至少一个非零的种子值")
                return
            
            encrypted_pil = Image.fromarray(processed_image)
            self.show_img(self.processed_image_label, encrypted_pil)
            
            self.processed_image = processed_image
            
            self.status_var.set(f"图片加密完成: {', '.join(encryption_steps)}")
        except Exception as e:
            messagebox.showerror("错误", f"加密图片时出错: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def decrypt_img(self):
        try:
            if self.current_image is None:
                messagebox.showwarning("警告", "请先加载图片")
                return
            
            processed_image = np.copy(self.current_image)
            height, width = processed_image.shape[:2]
            decryption_steps = []
            
            pixel_seed_str = self.pixel_seed_var.get()
            try:
                pixel_seed = float(pixel_seed_str)
                if pixel_seed != 0:
                    pixel_map_type = self.pixel_map_var.get()
                    chaotic_map, params = self.get_map(pixel_map_type)
                    processed_image = decrypt_pixels(processed_image, chaotic_map, pixel_seed, **params)
                    decryption_steps.append(f"像素值解密（{pixel_map_type}映射）")
            except ValueError:
                messagebox.showwarning("警告", f"无效的像素值种子: {pixel_seed_str}")
            
            row_seed = float(self.row_seed_var.get())
            col_seed = float(self.col_seed_var.get())
            
            if row_seed != 0 or col_seed != 0:
                perm_x = self.get_perm_img(width, "column")
                perm_y = self.get_perm_img(height, "row")
                
                if perm_x != list(range(width)) or perm_y != list(range(height)):
                    processed_image = decrypt_img(processed_image, perm_x, perm_y)
                    
                    if row_seed != 0 and col_seed != 0:
                        decryption_steps.append(f"位置解密（行列均已恢复）")
                    elif row_seed != 0:
                        decryption_steps.append(f"位置解密（仅行恢复）")
                    else:
                        decryption_steps.append(f"位置解密（仅列恢复）")
            
            if not decryption_steps:
                messagebox.showinfo("提示", "未执行任何解密操作，请设置至少一个非零的种子值")
                return
            
            decrypted_pil = Image.fromarray(processed_image)
            self.show_img(self.processed_image_label, decrypted_pil)
            
            self.processed_image = processed_image
            self.status_var.set(f"图片解密完成: {', '.join(decryption_steps)}")
            
        except Exception as e:
            messagebox.showerror("错误", f"解密图片时出错: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def clear_img(self):
        self.current_image = None
        if hasattr(self, 'processed_image'):
            del self.processed_image
        self.original_image_label.config(image='', text="选择图片或拖拽图片")
        self.processed_image_label.config(image='')
        self.status_var.set("准备就绪")
    
    def save_img(self):
        if not hasattr(self, 'processed_image'):
            messagebox.showwarning("警告", "没有可保存的图片")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")]
        )
        
        if file_path:
            try:
                Image.fromarray(self.processed_image).save(file_path)
                self.status_var.set(f"图片已保存至 {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存图片时出错: {str(e)}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    try:
        from tkinterdnd2 import DND_FILES, TkinterDnD
        root = TkinterDnD.Tk()
    except ImportError:
        messagebox.showwarning("警告", "tkinterdnd2库未安装，拖放功能不可用")
        root = tk.Tk()
    
    app = ChaoticCipherApp(root)
    root.mainloop() 
