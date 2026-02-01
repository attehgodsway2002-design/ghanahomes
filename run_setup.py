import subprocess
result = subprocess.run(['python', 'setup_admin.py'], capture_output=True, text=True, cwd=r'c:\Users\Huntsman\Desktop\rent app')
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
