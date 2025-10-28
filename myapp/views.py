# myapp/views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from .models import Student
from .forms import idpw
import os
import html


# 메인 선택 화면
def main(request):
    return render(request, 'index.html')


# 기존 index (하위 호환성)
def index(request):
    # 기존 index.html이 있었다면 그대로 사용
    return render(request, 'index.html')


# 인증 DB 데이터 목록
def student_list(request):
    students = Student.objects.all()
    return render(request, 'list.html', {'students': students})


# 1. SQL Injection
def sql_injection(request):
    if request.method == 'POST':
        form = idpw(request.POST)
        mode = request.POST.get('mode', 'safe')

        if form.is_valid():
            user_id = form.cleaned_data['id']
            password = form.cleaned_data['pw']

            with connection.cursor() as cursor:
                if mode == 'vulnerable':
                    # ❌ 취약한 코드 - SQL Injection 가능
                    sql_query = f"SELECT * FROM myapp_student WHERE userID='{user_id}' AND password='{password}'"
                    try:
                        cursor.execute(sql_query)
                        results = cursor.fetchall()

                        context = {
                            'mode': mode,
                            'executed_sql': sql_query,
                            'results': [f"ID: {r[0]}, UserID: {r[1]}, Password: {r[2]}" for r in results],
                        }
                    except Exception as e:
                        # SQL 오류 처리
                        context = {
                            'mode': mode,
                            'executed_sql': sql_query,
                            'results': [],
                            'message': f'SQL 실행 오류가 발생했습니다. 입력값을 확인해주세요.',
                            'error_detail': str(e) if mode == 'vulnerable' else None  # 취약 모드에서만 상세 오류 표시
                        }
                else:
                    # ✅ 안전한 코드 - Parameterized Query 사용
                    sql_query = "SELECT * FROM myapp_student WHERE userID=%s AND password=%s"
                    try:
                        cursor.execute(sql_query, (user_id, password))
                        results = cursor.fetchall()

                        context = {
                            'mode': mode,
                            'executed_sql': sql_query,
                            'params': f"({user_id}, {password})",
                            'results': [f"ID: {r[0]}, UserID: {r[1]}, Password: {r[2]}" for r in results],
                        }
                    except Exception as e:
                        # SQL 오류 처리
                        context = {
                            'mode': mode,
                            'executed_sql': sql_query,
                            'params': f"({user_id}, {password})",
                            'results': [],
                            'message': 'SQL 실행 오류가 발생했습니다. 입력값을 확인해주세요.'
                        }

                return render(request, 'success.html', context)
    else:
        form = idpw()

    return render(request, 'sql_injection.html', {'form': form})


# 2. Command Injection
def command_injection(request):
    if request.method == 'POST':
        command = request.POST.get('command', '').strip()
        mode = request.POST.get('mode', 'safe')

        if not command:
            context = {
                'mode': mode,
                'executed_sql': '입력 없음',
                'results': [],
                'message': '실행할 명령어를 입력해주세요.'
            }
            return render(request, 'success.html', context)

        if mode == 'vulnerable':
            # ❌ 취약한 코드 - eval() 직접 사용
            try:
                result = eval(command)
                executed_sql = f"eval('{command}')"
                results = [f"결과: {result}"]
                message = None
                error_detail = None
            except SyntaxError as e:
                executed_sql = f"eval('{command}')"
                results = []
                message = "문법 오류가 발생했습니다. Python 문법을 확인해주세요."
                error_detail = f"SyntaxError: {str(e)}"
            except NameError as e:
                executed_sql = f"eval('{command}')"
                results = []
                message = "정의되지 않은 변수나 함수를 사용했습니다."
                error_detail = f"NameError: {str(e)}"
            except Exception as e:
                executed_sql = f"eval('{command}')"
                results = []
                message = f"실행 중 오류가 발생했습니다: {type(e).__name__}"
                error_detail = str(e)
        else:
            # ✅ 안전한 코드 - 입력값 검증
            # 허용된 문자만 체크 (숫자, 연산자, 공백, 괄호)
            if not all(c in '0123456789+-*/(). ' for c in command):
                executed_sql = "입력 검증 실패"
                results = []
                message = "특수문자나 함수 호출이 포함되어 있어 실행이 거부되었습니다."
                error_detail = f"허용되지 않은 문자가 포함됨: {command}"
            else:
                try:
                    # 안전한 수식만 허용 (__builtins__ 제거)
                    result = eval(command, {"__builtins__": {}}, {})
                    executed_sql = f"eval('{command}') with restricted builtins"
                    results = [f"결과: {result}"]
                    message = None
                    error_detail = None
                except ZeroDivisionError:
                    executed_sql = f"eval('{command}')"
                    results = []
                    message = "0으로 나눌 수 없습니다."
                    error_detail = "ZeroDivisionError: division by zero"
                except Exception as e:
                    executed_sql = f"eval('{command}')"
                    results = []
                    message = "수식 계산 중 오류가 발생했습니다."
                    error_detail = f"{type(e).__name__}: {str(e)}"

        context = {
            'mode': mode,
            'executed_sql': executed_sql,
            'results': results,
            'message': message,
            'error_detail': error_detail if mode == 'vulnerable' else None
        }
        return render(request, 'success.html', context)

    return render(request, 'command_injection.html')


# 3. Directory Traversal
def directory_traversal(request):
    if request.method == 'POST':
        filename = request.POST.get('filename', '').strip()
        mode = request.POST.get('mode', 'safe')

        if not filename:
            context = {
                'mode': mode,
                'executed_sql': '입력 없음',
                'results': [],
                'message': '파일명을 입력해주세요.'
            }
            return render(request, 'success.html', context)

        # 테스트용 디렉토리 (실제로는 안전한 위치에 있어야 함)
        base_dir = '/tmp/uploads/'

        # 테스트 파일 생성
        try:
            os.makedirs(base_dir, exist_ok=True)
            test_file_path = os.path.join(base_dir, 'test.txt')
            if not os.path.exists(test_file_path):
                with open(test_file_path, 'w', encoding='utf-8') as f:
                    f.write('이것은 안전한 테스트 파일입니다.\n이 파일은 정상적으로 접근 가능합니다.')
        except Exception as e:
            context = {
                'mode': mode,
                'executed_sql': '테스트 환경 설정 실패',
                'results': [],
                'message': '테스트 환경을 준비하는 중 오류가 발생했습니다.'
            }
            return render(request, 'success.html', context)

        if mode == 'vulnerable':
            # ❌ 취약한 코드 - 경로 검증 없음
            file_path = base_dir + filename
            executed_sql = f"파일 경로: {file_path}"

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                results = [f"파일 내용:\n{content[:500]}"]  # 처음 500자만
                message = None
                error_detail = None
            except FileNotFoundError:
                results = []
                message = f"파일을 찾을 수 없습니다: {filename}"
                error_detail = f"FileNotFoundError: {file_path}"
            except PermissionError:
                results = []
                message = "파일에 접근할 권한이 없습니다."
                error_detail = f"PermissionError: {file_path}"
            except UnicodeDecodeError:
                results = []
                message = "텍스트 파일이 아니거나 인코딩 오류가 발생했습니다."
                error_detail = "UnicodeDecodeError: 바이너리 파일이거나 인코딩 문제"
            except Exception as e:
                results = []
                message = f"파일을 읽을 수 없습니다: {type(e).__name__}"
                error_detail = str(e)
        else:
            # ✅ 안전한 코드 - 경로 검증
            # 파일명에 .. 이나 / 가 있으면 거부
            if '..' in filename or '/' in filename or '\\' in filename:
                executed_sql = "입력 검증 실패"
                results = []
                message = "잘못된 파일명입니다. 경로 조작 문자(.., /, \\)가 포함되어 있습니다."
                error_detail = f"차단된 문자 포함: {filename}"
            else:
                # realpath로 실제 경로 확인
                file_path = os.path.join(base_dir, filename)
                real_path = os.path.realpath(file_path)
                real_base = os.path.realpath(base_dir)

                executed_sql = f"검증된 경로: {file_path}"

                if not real_path.startswith(real_base):
                    results = []
                    message = "접근이 거부되었습니다. 허용된 디렉토리 외부의 파일입니다."
                    error_detail = f"경로 벗어남: {real_path} not in {real_base}"
                else:
                    try:
                        with open(real_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        results = [f"파일 내용:\n{content[:500]}"]  # 처음 500자만
                        message = None
                        error_detail = None
                    except FileNotFoundError:
                        results = []
                        message = f"파일을 찾을 수 없습니다: {filename}"
                        error_detail = None
                    except Exception as e:
                        results = []
                        message = f"파일을 읽을 수 없습니다: {type(e).__name__}"
                        error_detail = None

        context = {
            'mode': mode,
            'executed_sql': executed_sql,
            'results': results,
            'message': message,
            'error_detail': error_detail if mode == 'vulnerable' else None
        }
        return render(request, 'success.html', context)

    return render(request, 'directory_traversal.html')


# 4. Reflected XSS
def reflected_xss(request):
    name = request.GET.get('name', '')
    mode = request.GET.get('mode', '')

    # views.py에서는 이스케이프 하지 않고 템플릿에 맡김
    context = {
        'name': name,
        'mode': mode,
    }
    return render(request, 'reflected_xss.html', context)


# 5. Stored XSS
# 간단한 메모리 저장소 (실제로는 DB 사용)
stored_comments = []


def stored_xss(request):
    global stored_comments

    if request.method == 'POST':
        # 모두 삭제
        if request.POST.get('clear'):
            stored_comments = []
            return redirect('stored_xss')

        author = request.POST.get('author', '')
        comment = request.POST.get('comment', '')
        mode = request.POST.get('mode', 'safe')

        if author and comment:
            stored_comments.append({
                'author': author,
                'text': comment,
                'is_safe': mode == 'safe'
            })

        return redirect('stored_xss')

    context = {
        'comments': stored_comments,
    }
    return render(request, 'stored_xss.html', context)

# 6. DOM-based XSS
def dom_xss(request):
    # DOM XSS는 클라이언트 측에서 처리되므로 서버는 단순히 템플릿만 반환
    return render(request, 'dom_xss.html')