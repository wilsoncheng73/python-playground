import streamlit as st
import psutil, platform, subprocess, shlex, os, time
import pkg_resources

st.set_page_config(page_title="公開多人共用 Python 平台", layout="wide")
st.title("🌐 公開多人共用 Python 平台 + 系統監控")

# ---------------------
# 訪客計數器
COUNTER_FILE = "/tmp/visitor_count.txt"
if os.path.exists(COUNTER_FILE):
    with open(COUNTER_FILE, "r") as f:
        count = int(f.read().strip())
else:
    count = 0

if "visited" not in st.session_state:
    count += 1
    st.session_state.visited = True
    with open(COUNTER_FILE, "w") as f:
        f.write(str(count))

st.markdown(f"👤 你是第 **{count}** 位訪客")
# ---------------------

# 左側：系統監控
col1, col2, col3 = st.columns([2,3,2])

with col1:
    st.subheader("💻 系統監控")
    st.text(f"作業系統: {platform.system()} {platform.release()}")
    st.text(f"架構: {platform.machine()}")
    st.text(f"Python版本: {platform.python_version()}")

    cpu_percents = psutil.cpu_percent(interval=1, percpu=True)
    st.text("CPU 使用率:")
    for i,p in enumerate(cpu_percents):
        st.text(f"核心 {i+1}: {p}%")
    st.text(f"平均 CPU 使用率: {psutil.cpu_percent()}%")

    mem = psutil.virtual_memory()
    st.text(f"記憶體: {round(mem.used/1024**3,2)}/{round(mem.total/1024**3,2)} GB ({mem.percent}%)")

    disk_texts = []
    for p in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(p.mountpoint)
            disk_texts.append(f"{p.device} ({p.mountpoint}): {round(usage.used/1024**3,2)}/{round(usage.total/1024**3,2)} GB ({usage.percent}%)")
        except PermissionError:
            continue
    st.text("磁碟使用:")
    for text in disk_texts:
        st.text(text)

    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        if gpus:
            st.text("GPU 使用:")
            for gpu in gpus:
                st.text(f"{gpu.name}: {gpu.memoryUsed}/{gpu.memoryTotal} MB ({round(gpu.load*100,2)}%)")
        else:
            st.text("無 GPU 或 GPUtil 未安裝")
    except:
        st.text("無 GPU 或 GPUtil 未安裝")

# 中間：共用程式碼編輯器
SHARED_PATH = "/tmp/shared_code.py"
if not os.path.exists(SHARED_PATH):
    with open(SHARED_PATH, "w") as f:
        f.write("# 在此編輯程式碼\n")

with open(SHARED_PATH, "r") as f:
    code = f.read()

with col2:
    st.subheader("💻 共用程式碼區")
    editor = st.text_area("共用程式碼編輯區", value=code, height=400)
    if st.button("儲存程式碼"):
        with open(SHARED_PATH, "w") as f:
            f.write(editor)
        st.success("程式碼已儲存")
    if st.button("執行程式碼"):
        with open("/tmp/run_code.py", "w") as f:
            f.write(editor)
        try:
            result = subprocess.run(["python3", "/tmp/run_code.py"], capture_output=True, text=True, timeout=20)
            st.subheader("執行結果")
            if result.stdout:
                st.code(result.stdout[:20000])
            if result.stderr:
                st.code(result.stderr[:20000])
        except subprocess.TimeoutExpired:
            st.error("程式執行超時")

# 右側：套件安裝
with col3:
    st.subheader("📦 套件安裝器")
    popular_packages = ["psutil", "numpy", "pandas", "matplotlib", "streamlit", "scipy", "requests", "GPUtil"]
    package_name = st.text_input("輸入套件名稱")
    selected_pkg = st.selectbox("熱門套件推薦", [""] + popular_packages)
    if selected_pkg:
        package_name = selected_pkg

    if st.button("安裝套件"):
        try:
            result = subprocess.run(["python3", "-m", "pip", "install", package_name], capture_output=True, text=True, timeout=60)
            st.subheader("安裝結果")
            if result.stdout:
                st.code(result.stdout[:20000])
            if result.stderr:
                st.code(result.stderr[:20000])
            if result.returncode == 0:
                st.success(f"{package_name} 安裝成功！")
            else:
                st.error(f"{package_name} 安裝失敗")
        except Exception as e:
            st.error(f"安裝錯誤: {e}")

    st.subheader("📦 系統已安裝套件")
    installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
    for i,(name,version) in enumerate(installed_packages.items()):
        if i>=50:
            st.text("...顯示部分套件（超過50個）...")
            break
        st.text(f"{name}=={version}")
