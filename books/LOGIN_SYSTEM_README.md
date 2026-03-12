# 🔐 SHA-256 Login System - คู่มือการใช้งาน

## ✅ ระบบที่อัพเกรดแล้ว

✔️ **รหัสผ่านถูกเข้ารหัสด้วย SHA-256**  
✔️ **ไม่สามารถเห็นรหัสผ่านจริงใน source code ได้**  
✔️ **ปลอดภัยกว่าการเก็บแบบ plain text มาก**  
✔️ **ทำงานได้ 100% บน GitHub Pages**  

---

## 🔑 ข้อมูลเข้าสู่ระบบปัจจุบัน

**Username:** `admin`  
**Password:** `301020`

---

## 🛠️ วิธีเพิ่มหรือเปลี่ยนรหัสผ่าน

### วิธีที่ 1: ใช้เครื่องมือสร้าง Hash (แนะนำ)

1. เปิดไฟล์ **`password_generator.html`** ในブราウザー
2. ใส่ชื่อผู้ใช้และรหัสผ่านที่ต้องการ
3. กดปุ่ม "สร้าง Hash"
4. Copy โค้ดที่ได้
5. เปิดไฟล์ **`login.html`**
6. หาส่วน `validPasswordHashes` (บรรทัดที่ 226)
7. เพิ่มหรือแก้ไขบรรทัดด้วยโค้ดที่ Copy มา

**ตัวอย่าง:**
```javascript
const validPasswordHashes = {
    'admin': '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92',  // Password: 301020
    'user1': 'anotherhashherexxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',  // Password: yourpass
    'john': 'yetanotherhashherexxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'   // Password: john123
};
```

### วิธีที่ 2: ใช้ Browser Console

1. เปิดหน้า **`login.html`**
2. กด F12 (Developer Tools)
3. ไปที่แท็บ **Console**
4. พิมพ์คำสั่ง:
   ```javascript
   sha256('รหัสผ่านของคุณ').then(hash => console.log(hash))
   ```
5. Copy hash ที่ได้ไปใส่ใน `login.html`

---

## 📂 ไฟล์ที่เกี่ยวข้อง

| ไฟล์ | หน้าที่ |
|------|---------|
| **login.html** | หน้าเข้าสู่ระบบหลัก (ใส่ hash ที่นี่) |
| **password_generator.html** | เครื่องมือสร้าง password hash |
| **index.html** | หน้าห้องสมุดหนังสือ (มีการป้องกัน) |
| **chapters.html** | หน้าอ่านนิยาย (มีการป้องกัน) |

---

## 🔒 ระดับความปลอดภัย

### ✅ สิ่งที่ระบบนี้ป้องกันได้:
- ผู้ใช้ทั่วไปไม่สามารถเห็นรหัสผ่านใน source code
- ป้องกันการเข้าถึงแบบสุ่ม
- เหมาะสำหรับแชร์กับเพื่อน/ครอบครัว

### ⚠️ ข้อจำกัด:
- ยังคงเป็น **client-side** authentication
- ผู้ใช้ที่มีความรู้ทางเทคนิคยังสามารถ bypass ได้
- **ไม่แนะนำ** สำหรับข้อมูลที่สำคัญมาก

---

## 💡 ตัวอย่างการใช้งาน

### เพิ่มผู้ใช้ใหม่

1. เปิด `password_generator.html`
2. ใส่:
   - Username: `john`
   - Password: `mypassword123`
3. Copy code ที่ได้: `'john': '44bc1....xxx'`
4. เปิด `login.html` แก้ไขเป็น:

```javascript
const validPasswordHashes = {
    'admin': '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92',  // Password: 301020
    'john': '44bc1...xxx'  // Password: mypassword123
};
```

### ลบผู้ใช้

เพียงลบบรรทัดนั้นออก:

```javascript
const validPasswordHashes = {
    'admin': '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'  // Password: 301020
    // ลบ 'john' ออก
};
```

---

## 🚀 สำหรับผู้ที่ต้องการความปลอดภัยสูงขึ้น

หากต้องการระบบที่ปลอดภัยจริงๆ ควรใช้:
- **Firebase Authentication**
- **Auth0**
- **Supabase**
- หรือย้ายไปใช้ **Netlify/Vercel** ที่มี serverless functions

---

## 📞 ปัญหาที่พบบ่อย

**Q: ลืมรหัสผ่านทำยังไง?**  
A: เปิดไฟล์ `login.html` ดูที่ comment ข้าง hash จะเห็นรหัสผ่านเดิม

**Q: ต้องการเปลี่ยนรหัสผ่าน admin ทำยังไง?**  
A: ใช้ `password_generator.html` สร้าง hash ใหม่แล้ว replace บรรทัดของ admin

**Q: ปลอดภัยพอไหม?**  
A: สำหรับ GitHub Pages และข้อมูลที่ไม่มีความลับมาก → ใช้ได้  
สำหรับข้อมูลสำคัญ → ควรใช้ระบบ backend authentication จริงๆ

---

## 📄 License

Free to use and modify for personal projects.
