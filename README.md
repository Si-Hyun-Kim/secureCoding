# Secure Coding Project

## 📁 Directory Structure

```
myproject/
├── myproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── myapp/
│   ├── migrations/
│   ├── static/
│   │   └── css/
│   │       ├── common.css             # 공통 스타일
│   │       ├── index.css              # 메인 화면 스타일
│   │       └── test-pages.css         # 테스트 페이지 스타일
│   ├── templates/
│   │   ├── index.html                # 메인 선택 화면
│   │   ├── sql_injection.html        # SQL Injection
│   │   ├── command_injection.html    # Command Injection
│   │   ├── directory_traversal.html  # Directory Traversal
│   │   ├── reflected_xss.html        # Reflected XSS
│   │   ├── stored_xss.html           # Stored XSS
│   │   ├── dom_xss.html              # DOM-based XSS
│   │   ├── list.html                 # DB 데이터 목록
│   │   └── success.html              # 결과 페이지
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
└── manage.py
```

## ▶️ 실행 방법

### 1. `Python 3.13` 설치
- `Python 3.14`는 아직 `mysqlclient`를 공식적으로 사용하지 못하므로, 반드시 `3.13` 버전으로 설치 권장

### 2. 가상환경 구동
```bash
py -m venv venv
./venv/scripts/activate   # 가상환경 실행
```

### 3. 필요한 Python 라이브러리 설치
```bash
pip install django mysqlclient
pip list    # 설치 확인
```

### 4. MySQL Workbench에서 DB 생성
```SQL
CREATE DATABASE student;      # student DB 생성
```

### 5. 마이그레이션
```bash
py manage.py makemigrations   # 마이그레이션 파일 생성
py manage.py migrate          # 마이그레이션
py manage.py showmigrations   # 마이그레이션 적용 여부 확인
```

### 6. Create superuser
```bash
py manage.py createsuperuser
```

### 7. 서버 실행
```bash
py manage.py runserver
```

### 8. 브라우저에서 접속
```
http://localhost:8000/myapp/
```

## 사용 방법

### 메인 화면
- `localhost:8000/myapp/` - 6개의 보안 취약점을 선택할 수 있는 메인 화면

### 각 보안 취약점 테스트
1. **SQL Injection** (`/myapp/sql-injection/`)
   - User ID: `admin' OR '1'='1`
   - Password: `아무거나`

2. **Command Injection** (`/myapp/command-injection/`)
   - 정상: `2 + 3`
   - 공격: `__import__('os').system('whoami')`

3. **Directory Traversal** (`/myapp/directory-traversal/`)
   - 정상: `test.txt`
   - 공격: `../../etc/passwd`

4. **Reflected XSS** (`/myapp/reflected-xss/`)
   - 정상: `홍길동`
   - 공격: `<script>alert('XSS')</script>`

5. **Stored XSS** (`/myapp/stored-xss/`)
   - 댓글에 스크립트 삽입: `<script>alert('저장된 XSS')</script>`

6. **DOM-based XSS** (`/myapp/dom-xss/`)
   - URL: `?name=<img src=x onerror=alert('XSS')>`


## 주요 변경 사항

### 1. URL 구조
- 메인 화면: `/myapp/` (index)
- 각 테스트: `/myapp/[취약점명]/`

### 2. 템플릿 구조
- `index.html`: 메인 선택 화면
- `sql_injection.html`: 기존 `index.html`을 개선한 버전
- 5개의 새로운 템플릿 추가

### 3. Views 함수
- `index()`: 메인 화면
- `sql_injection()`: SQL Injection 테스트
- `command_injection()`: Command Injection 테스트
- `directory_traversal()`: Directory Traversal 테스트
- `reflected_xss()`: Reflected XSS 테스트
- `stored_xss()`: Stored XSS 테스트 (메모리 기반)
- `dom_xss()`: DOM-based XSS 테스트

## ⚠️ 주의사항

1. **개발 환경 전용**
   - 이 코드는 교육 목적으로 의도적으로 취약한 코드를 포함하고 있습니다.
   - 실제 운영 환경에서는 절대 사용하지 마세요.

2. **Stored XSS**
   - 현재 메모리에 저장되므로 서버 재시작 시 데이터가 사라집니다.
   - 실제 DB 저장이 필요하면 모델을 추가하세요.

3. **Directory Traversal**
   - `/tmp/uploads/` 디렉토리를 사용합니다.
   - 테스트 파일이 자동으로 생성됩니다.

## 자료

- SQL Injection: Parameterized Query 사용
- Command Injection: 입력값 검증, eval() 사용 금지
- Directory Traversal: 경로 정규화, 베이스 디렉토리 검증
- XSS: HTML 이스케이프, textContent 사용

## Trouble Shooting

### ImportError 발생 시
```bash
# forms.py가 없는 경우
python manage.py makemigrations
python manage.py migrate
```

### 템플릿을 찾을 수 없는 경우
- `myapp/templates/` 디렉토리가 존재하는지 확인
- `settings.py`의 `INSTALLED_APPS`에 `myapp`이 등록되어 있는지 확인

### 404 Error 발생 시
- URL 패턴이 올바른지 확인: `/myapp/` (끝에 슬래시)
- `myproject/urls.py`에 `include('myapp.urls')`가 있는지 확인

## Support

문제가 발생하면 다음을 확인하세요:
1. Python 버전 (3.8 이상 권장)
2. Django 버전 (3.2 이상 권장)
3. 모든 파일이 올바른 위치에 있는지
4. 서버 로그 메시지