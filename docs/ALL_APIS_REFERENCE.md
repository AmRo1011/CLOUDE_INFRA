# 📚 دليل كامل لكل APIs في المشروع

## 🌐 Base URLs

### محلي (Local Development):
- **عبر Gateway**: `http://127.0.0.1` (Nginx)
- **مباشر**:
  - User Management: `http://localhost:8001`
  - Chat: `http://localhost:8004`
  - Document: `http://localhost:8002`
  - Quiz: `http://localhost:8003`

### AWS (Production):
- `https://your-domain.com` (حسب الـ deployment)

---

## 1️⃣ User Management Service (Port 8001)

### 🔐 Authentication Endpoints (`/api/auth`)

| Method | Endpoint | الوصف | يحتاج Auth | الصلاحية المطلوبة |
|--------|----------|-------|-----------|-------------------|
| POST | `/api/auth/register` | تسجيل مستخدم جديد | ❌ | - |
| POST | `/api/auth/login` | تسجيل دخول والحصول على JWT | ❌ | - |
| POST | `/api/auth/logout` | تسجيل خروج | ✅ | - |
| POST | `/api/auth/refresh` | تجديد الـ token | ✅ | - |
| GET | `/api/auth/health` | Health check | ❌ | - |

#### مثال: تسجيل مستخدم جديد
```powershell
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1/api/auth/register" `
  -ContentType "application/json" `
  -Body (@{
    email = "student@example.com"
    password = "SecurePass123!"
    full_name = "Ahmed Mohamed"
    role = "student"
  } | ConvertTo-Json)
```

#### مثال: تسجيل الدخول
```powershell
$response = Invoke-RestMethod -Method POST -Uri "http://127.0.0.1/api/auth/login" `
  -ContentType "application/json" `
  -Body (@{
    email = "student@example.com"
    password = "SecurePass123!"
  } | ConvertTo-Json)

$token = $response.data.access_token
```

---

### 👤 User Management Endpoints (`/api/users`)

| Method | Endpoint | الوصف | يحتاج Auth | الصلاحية المطلوبة |
|--------|----------|-------|-----------|-------------------|
| GET | `/api/users/me` | معلومات المستخدم الحالي | ✅ | - |
| PUT | `/api/users/me` | تحديث معلومات المستخدم | ✅ | - |
| GET | `/api/users/` | قائمة جميع المستخدمين | ✅ | `user.manage` (admin) |
| GET | `/api/users/{user_id}` | معلومات مستخدم محدد | ✅ | `user.manage` (admin) |
| PUT | `/api/users/{user_id}/role` | تغيير دور المستخدم | ✅ | `user.manage` (admin) |
| DELETE | `/api/users/{user_id}` | حذف مستخدم | ✅ | `user.manage` (admin) |

#### مثال: الحصول على معلوماتك
```powershell
$headers = @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Method GET -Uri "http://127.0.0.1/api/users/me" -Headers $headers
```

#### مثال: قائمة المستخدمين (admin فقط)
```powershell
Invoke-RestMethod -Method GET -Uri "http://127.0.0.1/api/users/?page=1&limit=20&role=student" -Headers $headers
```

---

## 2️⃣ Chat Service (Port 8004)

### 💬 Conversation Endpoints (`/api/chat`)

| Method | Endpoint | الوصف | يحتاج Auth |
|--------|----------|-------|-----------|
| POST | `/api/chat/conversations` | إنشاء محادثة جديدة | ✅ |
| GET | `/api/chat/conversations` | قائمة محادثاتك | ✅ |
| GET | `/api/chat/conversations/{id}` | تفاصيل محادثة محددة | ✅ |
| DELETE | `/api/chat/conversations/{id}` | حذف محادثة | ✅ |
| POST | `/api/chat/conversations/{id}/context` | إضافة مستند كسياق للمحادثة | ✅ |

#### مثال: إنشاء محادثة جديدة
```powershell
$conversation = Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1/api/chat/conversations" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body (@{ title = "مساعدة في الفيزياء" } | ConvertTo-Json)

$convId = $conversation.data.id
```

#### مثال: إضافة مستند كسياق
```powershell
Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1/api/chat/conversations/$convId/context" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body (@{ document_id = "uuid-of-document" } | ConvertTo-Json)
```

---

### 💭 Message Endpoints (`/api/chat`)

| Method | Endpoint | الوصف | يحتاج Auth |
|--------|----------|-------|-----------|
| POST | `/api/chat/conversations/{id}/messages` | إرسال رسالة والحصول على رد AI | ✅ |

#### مثال: إرسال رسالة
```powershell
$response = Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1/api/chat/conversations/$convId/messages" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body (@{ content = "اشرح لي قانون نيوتن الأول" } | ConvertTo-Json)

# الرد بيحتوي على رسالتك + رد الـ AI
$userMsg = $response.data.user_message
$aiMsg = $response.data.assistant_message
```

---

## 3️⃣ Document Service (Port 8002)

### 📄 Document Endpoints (`/api/documents`)

| Method | Endpoint | الوصف | يحتاج Auth | الصلاحية المطلوبة |
|--------|----------|-------|-----------|-------------------|
| POST | `/api/documents/upload` | رفع مستند جديد | ✅ | `document.upload` |
| GET | `/api/documents/` | قائمة مستنداتك | ✅ | - |
| GET | `/api/documents/{id}` | تفاصيل مستند محدد | ✅ | - |
| GET | `/api/documents/{id}/download` | رابط تحميل المستند | ✅ | - |
| GET | `/api/documents/{id}/content` | النص المستخرج من المستند | ✅ | - |
| DELETE | `/api/documents/{id}` | حذف مستند | ✅ | `document.delete` |

#### مثال: رفع مستند
```powershell
# إنشاء form data
$filePath = "C:\path\to\file.pdf"
$fileName = [System.IO.Path]::GetFileName($filePath)
$fileBytes = [System.IO.File]::ReadAllBytes($filePath)

# إرسال باستخدام Invoke-WebRequest
$boundary = [System.Guid]::NewGuid().ToString()
$headers["Content-Type"] = "multipart/form-data; boundary=$boundary"

# أو استخدم curl (أسهل):
curl.exe -X POST "http://127.0.0.1/api/documents/upload" `
  -H "Authorization: Bearer $token" `
  -F "file=@C:\path\to\file.pdf" `
  -F "title=كتاب الفيزياء" `
  -F "description=فصل الميكانيكا"
```

#### مثال: قائمة المستندات
```powershell
Invoke-RestMethod -Method GET `
  -Uri "http://127.0.0.1/api/documents/?page=1&limit=20&status=completed" `
  -Headers $headers
```

#### مثال: الحصول على محتوى المستند
```powershell
$content = Invoke-RestMethod -Method GET `
  -Uri "http://127.0.0.1/api/documents/$documentId/content" `
  -Headers $headers
```

---

### 📝 Notes Endpoints (`/api/documents`)

| Method | Endpoint | الوصف | يحتاج Auth |
|--------|----------|-------|-----------|
| POST | `/api/documents/{id}/notes` | إنشاء ملاحظة يدوية | ✅ |
| GET | `/api/documents/{id}/notes` | قائمة الملاحظات | ✅ |
| POST | `/api/documents/{id}/generate-notes` | توليد ملاحظات تلقائيًا بالـ AI | ✅ |

#### مثال: توليد ملاحظات تلقائيًا
```powershell
$notes = Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1/api/documents/$documentId/generate-notes" `
  -Headers $headers

Write-Host $notes.data.content
```

#### مثال: إنشاء ملاحظة يدوية
```powershell
Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1/api/documents/$documentId/notes" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body (@{
    title = "ملخص الفصل الأول"
    content = "النقاط الرئيسية: ..."
  } | ConvertTo-Json)
```

---

## 4️⃣ Quiz Service (Port 8003)

### 📝 Quiz Endpoints (`/api/quiz`)

| Method | Endpoint | الوصف | يحتاج Auth | الصلاحية المطلوبة |
|--------|----------|-------|-----------|-------------------|
| POST | `/api/quiz/generate` | توليد اختبار من مستند | ✅ | `quiz.create` |
| GET | `/api/quiz/` | قائمة الاختبارات المتاحة | ✅ | - |
| GET | `/api/quiz/{id}` | تفاصيل اختبار محدد | ✅ | - |
| PUT | `/api/quiz/{id}` | تحديث إعدادات اختبار | ✅ | `quiz.create` |
| DELETE | `/api/quiz/{id}` | حذف اختبار | ✅ | `quiz.create` |

#### مثال: توليد اختبار من مستند
```powershell
$quiz = Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1/api/quiz/generate" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body (@{
    document_id = "uuid-of-document"
    title = "اختبار الفصل الأول"
    num_questions = 10
    question_types = @("multiple_choice", "true_false")
    time_limit_minutes = 30
  } | ConvertTo-Json)

$quizId = $quiz.data.quiz_id
```

#### مثال: قائمة الاختبارات
```powershell
Invoke-RestMethod -Method GET `
  -Uri "http://127.0.0.1/api/quiz/?page=1&limit=20&status=published" `
  -Headers $headers
```

#### مثال: الحصول على تفاصيل اختبار
```powershell
# للطلاب: الإجابات الصحيحة مخفية
# للمدرسين والـ admins: الإجابات ظاهرة
$quizDetails = Invoke-RestMethod -Method GET `
  -Uri "http://127.0.0.1/api/quiz/$quizId" `
  -Headers $headers
```

---

### ✍️ Quiz Attempt Endpoints (`/api/quiz`)

| Method | Endpoint | الوصف | يحتاج Auth | الصلاحية المطلوبة |
|--------|----------|-------|-----------|-------------------|
| POST | `/api/quiz/{id}/start` | بدء محاولة جديدة | ✅ | `quiz.take` |
| POST | `/api/quiz/{id}/attempts/{attempt_id}/answer` | إرسال إجابة لسؤال | ✅ | - |
| POST | `/api/quiz/{id}/attempts/{attempt_id}/submit` | تسليم الاختبار للتصحيح | ✅ | - |
| GET | `/api/quiz/{id}/attempts` | قائمة محاولاتك | ✅ | - |

#### مثال: بدء اختبار
```powershell
$attempt = Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1/api/quiz/$quizId/start" `
  -Headers $headers

$attemptId = $attempt.data.attempt_id
$timeRemaining = $attempt.data.time_remaining_seconds
Write-Host "الوقت المتبقي: $timeRemaining ثانية"
```

#### مثال: إرسال إجابة
```powershell
Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1/api/quiz/$quizId/attempts/$attemptId/answer" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body (@{
    question_id = "uuid-of-question"
    selected_option_id = "uuid-of-selected-option"
  } | ConvertTo-Json)
```

#### مثال: تسليم الاختبار
```powershell
$result = Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1/api/quiz/$quizId/attempts/$attemptId/submit" `
  -Headers $headers

Write-Host "النتيجة: $($result.data.score)%"
Write-Host "عدد الإجابات الصحيحة: $($result.data.correct_answers)"
```

---

## 🔐 Authentication Header

جميع الـ endpoints اللي محتاجة authentication، لازم تبعت الـ token في الـ header:

```powershell
$headers = @{
    Authorization = "Bearer YOUR_JWT_TOKEN_HERE"
}

Invoke-RestMethod -Uri "URL" -Headers $headers
```

---

## 👥 User Roles & Permissions

### الأدوار المتاحة:
1. **admin** - كل الصلاحيات
2. **instructor** - إنشاء محتوى واختبارات
3. **student** - الوصول للمحتوى وأخذ الاختبارات

### الصلاحيات حسب الدور:

| الصلاحية | admin | instructor | student |
|---------|-------|------------|---------|
| `user.manage` | ✅ | ❌ | ❌ |
| `document.upload` | ✅ | ✅ | ❌ |
| `document.delete` | ✅ | ✅ | ❌ |
| `quiz.create` | ✅ | ✅ | ❌ |
| `quiz.take` | ✅ | ✅ | ✅ |

---

## 🔍 Swagger Documentation

كل service عنده Swagger UI خاص بيه:

- User Management: http://localhost:8001/docs
- Chat: http://localhost:8004/docs
- Document: http://localhost:8002/docs
- Quiz: http://localhost:8003/docs

---

## 🧪 سيناريو كامل للاختبار

```powershell
# 1. تسجيل طالب جديد
$signup = Invoke-RestMethod -Method POST -Uri "http://127.0.0.1/api/auth/register" `
  -ContentType "application/json" `
  -Body (@{
    email = "student@test.com"
    password = "Test123!"
    full_name = "Ahmed Test"
    role = "student"
  } | ConvertTo-Json)

# 2. تسجيل الدخول
$login = Invoke-RestMethod -Method POST -Uri "http://127.0.0.1/api/auth/login" `
  -ContentType "application/json" `
  -Body (@{ email = "student@test.com"; password = "Test123!" } | ConvertTo-Json)

$token = $login.data.access_token
$headers = @{ Authorization = "Bearer $token" }

# 3. الحصول على قائمة الاختبارات المتاحة
$quizzes = Invoke-RestMethod -Method GET `
  -Uri "http://127.0.0.1/api/quiz/" `
  -Headers $headers

$quizId = $quizzes.data.quizzes[0].id

# 4. بدء اختبار
$attempt = Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1/api/quiz/$quizId/start" `
  -Headers $headers

$attemptId = $attempt.data.attempt_id

# 5. الحصول على أسئلة الاختبار
$quiz = Invoke-RestMethod -Method GET `
  -Uri "http://127.0.0.1/api/quiz/$quizId" `
  -Headers $headers

# 6. إرسال إجابات
foreach ($question in $quiz.data.questions) {
    Invoke-RestMethod -Method POST `
      -Uri "http://127.0.0.1/api/quiz/$quizId/attempts/$attemptId/answer" `
      -Headers $headers `
      -ContentType "application/json" `
      -Body (@{
        question_id = $question.id
        selected_option_id = $question.options[0].id
      } | ConvertTo-Json)
}

# 7. تسليم الاختبار
$result = Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1/api/quiz/$quizId/attempts/$attemptId/submit" `
  -Headers $headers

Write-Host "=== النتيجة النهائية ===" -ForegroundColor Green
Write-Host "الدرجة: $($result.data.score)%" -ForegroundColor Cyan
Write-Host "الإجابات الصحيحة: $($result.data.correct_answers) من $($result.data.total_questions)" -ForegroundColor Cyan
```

---

## 📋 Status Codes

| Code | المعنى |
|------|--------|
| 200 | نجح الطلب |
| 201 | تم الإنشاء بنجاح |
| 202 | تم قبول الطلب (معالجة async) |
| 400 | خطأ في البيانات المرسلة |
| 401 | غير مصرح (token مفقود أو منتهي) |
| 403 | ممنوع (لا تملك الصلاحية) |
| 404 | غير موجود |
| 500 | خطأ في السيرفر |

---

## 🎯 ملاحظات مهمة

1. **كل الـ responses بتيجي بالشكل ده**:
```json
{
  "status": "success",
  "data": { ... },
  "message": "..."
}
```

2. **Pagination في القوائم**:
- استخدم `?page=1&limit=20` في أي endpoint بيرجع قائمة

3. **Filtering**:
- معظم القوائم بتقبل filters زي `?status=published&role=student`

4. **الوقت**:
- كل التواريخ بتيجي بصيغة ISO 8601: `2025-12-04T16:30:00Z`

5. **الـ UUIDs**:
- كل الـ IDs في المشروع بصيغة UUID v4

