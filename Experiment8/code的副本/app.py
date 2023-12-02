import os
import subprocess
import shutil

directory_path = './data'
script_path = './main.sh'
replace_path = './scripts/replace.sh'
result_path = './result'

# 打开所有文件
def open_directory():
    for root, dirs, files in sorted(os.walk(directory_path)):
        for file in files:
            news_list_file_path = root + '/' + file
            run_script(news_list_file_path, root + '/')

def test():
    news_list_file_path = './data/2023-11-23-08/index.json'
    run_script(news_list_file_path, './data/2023-11-23-08')

def run_script(news_list_file_path, root_path):
    try:
        subprocess.run(['bash', script_path, news_list_file_path, root_path], text=True, capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

def replace():
    subprocess.run(['bash', replace_path], text=True, capture_output=True, check=True)

def delete_result():
    shutil.rmtree(result_path)

if __name__ == '__main__':
    delete_result()
    # open_directory()
    open_directory()
    replace()