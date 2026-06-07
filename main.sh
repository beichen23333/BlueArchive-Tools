#!/bin/bash

C_DEF='\033[0m'
C_ACCENT='\033[38;5;111m'
C_OK='\033[32m'
C_WARN='\033[33m'
C_ERR='\033[31m'
C_TITLE='\033[1;36m'

CONFIG_FILE=".script_cfg"

if [ -f "$CONFIG_FILE" ]; then
    LANG_TYPE=$(cat "$CONFIG_FILE")
else
    case "$LANG" in
        *zh_*) LANG_TYPE="CN" ;;
        *ja_*) LANG_TYPE="JP" ;;
        *vi_*) LANG_TYPE="VN" ;;
        *) LANG_TYPE="CN" ;;
    esac
    echo "$LANG_TYPE" > "$CONFIG_FILE"
fi

get_text() {
    local key=$1
    case $LANG_TYPE in
        "CN")
            case $key in
                "TITLE") echo "主控制脚本" ;;
                "CHECKING") echo "正在检查环境..." ;;
                "MISSING") echo "检测到以下依赖缺失:" ;;
                "INSTALLING") echo "正在处理安装，请稍候..." ;;
                "EXIT") echo "退出脚本" ;;
                "BACK") echo "返回上级菜单" ;;
                "SUB_MAIN") echo "主功能菜单" ;;
                "ASSIST") echo "辅助功能菜单" ;;
                "DEP_MENU") echo "安装依赖菜单" ;;
                "LANG_SET") echo "语言设置 / Language Settings" ;;
                "PACK_APK") echo "打包 APK" ;;
                "PROCESS_EXCEL") echo "处理ExcelDB.db和Excel.zip" ;;
                "SDK_PROMPT") echo "输入SDKURL (留空跳过): " ;;
                "CFG_PROMPT") echo "是否修改GameMainConfig? (y/n): " ;;
                "FIELDS_PROMPT") echo "请输入字段名(逗号隔开): " ;;
                "VALUE_PROMPT") echo "请输入 %s 的值: " ;;
                "COEXIST_PROMPT") echo "是否使用共存包? (y/n): " ;;
                "TRUST_PROMPT") echo "是否信任ca证书? (y/n): " ;;
                "LOGIN_PROMPT") echo "是否修改登录文本为中文? (y/n): " ;;
                "CLONING") echo "正在从 GitHub 克隆..." ;;
                "RUNNING_CMD") echo "执行命令: %s" ;;
                "DONE_RETURN") echo "按任意键返回..." ;;
                "INVALID_INPUT") echo "输入无效，请重新输入。" ;;
                "SERVER_PROMPT") echo "请选择服务器 (CN/JP/GL): " ;;
                "MODE_PROMPT") echo "请选择模式 (Extract / Repack): " ;;
                "TABLE_FOLDER_PROMPT") echo "请输入 ExcelDB.db 和 Excel.zip 所在的目录: " ;;
                "TABLE_FOLDER_ERR") echo "警告：该目录下未找到 ExcelDB.db 或 Excel.zip！" ;;
                "OUT_JSON_PROMPT") echo "请输入输出的 JSON 文件夹目录: " ;;
                "IN_JSON_PROMPT") echo "请输入要打包的 JSON 文件夹目录 (内需包含 Excel 和 ExcelDB 文件夹): " ;;
                "IN_JSON_ERR") echo "警告：打包目标目录内必须包含 'Excel' 或 'ExcelDB' 子文件夹！" ;;
                "DB_KEY_PROMPT") echo "请输入 DB 密钥 (留空则不需要): " ;;
                "CATALOG_PROMPT") echo "是否修改 TableCatalog? (y/n): " ;;
                "NAME_PROMPT") echo "是否混淆文件名? (y/n): " ;;
                "PY_NOT_FOUND") echo "未检测到 Python，正在尝试自动安装..." ;;
                "SCRIPT_NOT_FOUND") echo "错误: 未找到脚本 %s！" ;;
                "GET_CATALOG") echo "获取 Catalog" ;;
                "GET_FILES") echo "下载文件" ;;
                "GET_VERSION") echo "获取当前版本号" ;;
                "UPDATE_ENV") echo "更新 env 配置" ;;
                "TYPE_PROMPT") echo "请选择资源类型 (Table/Media/Bundle): " ;;
                "CLIENT_PROMPT") echo "请选择客户端平台 (Android/iOS/Windows): " ;;
                "FILES_PROMPT") echo "请输入要下载的文件名列表 (逗号隔开，例如 ExcelDB.db,Excel.zip): " ;;
                "IS_FULL_VERSION") echo "是否包含小版本号? (y/n): " ;;
                "VERSION_KEY_PROMPT") echo "请选择特定版本号 Key (TableVersion/MediaVersion/PatchVersion/ResourceVersion): " ;;
                "FLATDATA_BRANCH_PROMPT") echo "请选择 FlatData 分支区域 (CN/GL/JP): " ;;
                "DEP_OPT_1") echo "检查/同步 Git 子模块 (crcmanip, PyCriCodecs)" ;;
                "DEP_OPT_2") echo "检查并安装 requirements.txt 缺失的 pip 库" ;;
                "DEP_OPT_3") echo "安装配置 sqlcipher" ;;
                "DEP_OPT_4") echo "克隆 BAJpApkSrc" ;;
                "DEP_OPT_5") echo "克隆 BA-FlatData" ;;
                "DEP_OPT_ALL") echo "一键安装所有依赖" ;;
                "SUBMODULE_START") echo "开始检查并同步 Git 子模块..." ;;
                "SUBMODULE_DONE") echo "子模块处理完毕。" ;;
                "REQ_START") echo "开始分析并补全 requirements.txt 依赖..." ;;
                "REQ_MISSING") echo "正在为您单独安装缺失的库: %s" ;;
                "REQ_ALL_INSTALLED") echo "requirements.txt 中的所有库均已安装。" ;;
                "REQ_NOT_FOUND") echo "未找到 requirements.txt 文件！" ;;
                "SQLCIPHER_START") echo "开始配置 sqlcipher 编译环境..." ;;
                "SQLCIPHER_PIP") echo "正在安装 pysqlcipher3..." ;;
                "SQLCIPHER_DONE") echo "sqlcipher 组件配置完成。" ;;
                "FLATDATA_START") echo "正在克隆 BA-FlatData 仓库的 %s 分支..." ;;
                "FLATDATA_DONE") echo "FlatData 克隆完毕。" ;;
            esac
            ;;
        "EN")
            case $key in
                "TITLE") echo "Main Control Script" ;;
                "CHECKING") echo "Checking environment..." ;;
                "MISSING") echo "The following dependencies are missing:" ;;
                "INSTALLING") echo "Processing installation, please wait..." ;;
                "EXIT") echo "Exit Script" ;;
                "BACK") echo "Back to Previous Menu" ;;
                "SUB_MAIN") echo "Main Features Menu" ;;
                "ASSIST") echo "Assistant Features Menu" ;;
                "DEP_MENU") echo "Dependency Installation Menu" ;;
                "LANG_SET") echo "Language Settings" ;;
                "PACK_APK") echo "Pack APK" ;;
                "PROCESS_EXCEL") echo "Process ExcelDB.db & Excel.zip" ;;
                "SDK_PROMPT") echo "Enter SDKURL (leave empty to skip): " ;;
                "CFG_PROMPT") echo "Modify GameMainConfig? (y/n): " ;;
                "FIELDS_PROMPT") echo "Enter field names (separated by commas): " ;;
                "VALUE_PROMPT") echo "Enter value for %s: " ;;
                "COEXIST_PROMPT") echo "Use coexistence package? (y/n): " ;;
                "TRUST_PROMPT") echo "Trust CA certificate? (y/n): " ;;
                "LOGIN_PROMPT") echo "Change login text to Chinese? (y/n): " ;;
                "CLONING") echo "Cloning from GitHub..." ;;
                "RUNNING_CMD") echo "Executing command: %s" ;;
                "DONE_RETURN") echo "Press any key to return..." ;;
                "INVALID_INPUT") echo "Invalid input, please try again." ;;
                "SERVER_PROMPT") echo "Select server (CN/JP/GL): " ;;
                "MODE_PROMPT") echo "Select mode (Extract / Repack): " ;;
                "TABLE_FOLDER_PROMPT") echo "Enter directory of ExcelDB.db and Excel.zip: " ;;
                "TABLE_FOLDER_ERR") echo "Warning: ExcelDB.db or Excel.zip not found in this directory!" ;;
                "OUT_JSON_PROMPT") echo "Enter output JSON directory: " ;;
                "IN_JSON_PROMPT") echo "Enter directory of JSON to pack (must contain Excel/ExcelDB subfolders): " ;;
                "IN_JSON_ERR") echo "Warning: Target directory must contain 'Excel' or 'ExcelDB' subfolders!" ;;
                "DB_KEY_PROMPT") echo "Enter DB Key (leave empty if not needed): " ;;
                "CATALOG_PROMPT") echo "Modify TableCatalog? (y/n): " ;;
                "NAME_PROMPT") echo "Obfuscate filenames? (y/n): " ;;
                "PY_NOT_FOUND") echo "Python not detected, attempting auto-installation..." ;;
                "SCRIPT_NOT_FOUND") echo "Error: Script %s not found!" ;;
                "GET_CATALOG") echo "Get Catalog" ;;
                "GET_FILES") echo "Download Files" ;;
                "GET_VERSION") echo "Get Current Version" ;;
                "UPDATE_ENV") echo "Update Env Configuration" ;;
                "TYPE_PROMPT") echo "Select resource type (Table/Media/Bundle): " ;;
                "CLIENT_PROMPT") echo "Select client platform (Android/iOS/Windows): " ;;
                "FILES_PROMPT") echo "Enter filenames to download (separated by commas, e.g., ExcelDB.db,Excel.zip): " ;;
                "IS_FULL_VERSION") echo "Include sub-version number? (y/n): " ;;
                "VERSION_KEY_PROMPT") echo "Select specific version Key (TableVersion/MediaVersion/PatchVersion/ResourceVersion): " ;;
                "FLATDATA_BRANCH_PROMPT") echo "Select FlatData branch region (CN/GL/JP): " ;;
                "DEP_OPT_1") echo "Check/Sync Git Submodules (crcmanip, PyCriCodecs)" ;;
                "DEP_OPT_2") echo "Check & Install Missing Pip Libraries (requirements.txt)" ;;
                "DEP_OPT_3") echo "Install & Configure sqlcipher" ;;
                "DEP_OPT_4") echo "Clone BAJpApkSrc" ;;
                "DEP_OPT_5") echo "Clone BA-FlatData" ;;
                "DEP_OPT_ALL") echo "One-click Install All Dependencies" ;;
                "SUBMODULE_START") echo "Starting to check and sync Git submodules..." ;;
                "SUBMODULE_DONE") echo "Submodules processed successfully." ;;
                "REQ_START") echo "Starting to analyze and install missing requirements.txt dependencies..." ;;
                "REQ_MISSING") echo "Installing missing library individually: %s" ;;
                "REQ_ALL_INSTALLED") echo "All libraries in requirements.txt are already installed." ;;
                "REQ_NOT_FOUND") echo "requirements.txt file not found!" ;;
                "SQLCIPHER_START") echo "Starting to configure sqlcipher compilation environment..." ;;
                "SQLCIPHER_PIP") echo "Installing pysqlcipher3..." ;;
                "SQLCIPHER_DONE") echo "sqlcipher components configuration completed." ;;
                "FLATDATA_START") echo "Cloning branch %s of BA-FlatData repository..." ;;
                "FLATDATA_DONE") echo "FlatData cloning completed." ;;
            esac
            ;;
        "JP")
            case $key in
                "TITLE") echo "メイン制御スクリプト" ;;
                "CHECKING") echo "環境をチェック中..." ;;
                "MISSING") echo "以下の依存関係が不足しています:" ;;
                "INSTALLING") echo "インストールを処理中、しばらくお待ちください..." ;;
                "EXIT") echo "スクリプトを終了" ;;
                "BACK") echo "前のメニューに戻る" ;;
                "SUB_MAIN") echo "メイン機能メニュー" ;;
                "ASSIST") echo "補助機能メニュー" ;;
                "DEP_MENU") echo "依存関係インストールメニュー" ;;
                "LANG_SET") echo "言語設定 / Language Settings" ;;
                "PACK_APK") echo "APK をビルド" ;;
                "PROCESS_EXCEL") echo "ExcelDB.db と Excel.zip の処理" ;;
                "SDK_PROMPT") echo "SDKURL を入力 (スキップする場合は空欄): " ;;
                "CFG_PROMPT") echo "GameMainConfig を変更しますか？ (y/n): " ;;
                "FIELDS_PROMPT") echo "フィールド名を入力してください (カンマ区切り): " ;;
                "VALUE_PROMPT") echo "%s の値を入力してください: " ;;
                "COEXIST_PROMPT") echo "共存パッケージを使用しますか？ (y/n): " ;;
                "TRUST_PROMPT") echo "CA証明書を信頼しますか？ (y/n): " ;;
                "LOGIN_PROMPT") echo "ログインテキストを中国語に変更しますか？ (y/n): " ;;
                "CLONING") echo "GitHub からクローン中..." ;;
                "RUNNING_CMD") echo "コマンドを実行中: %s" ;;
                "DONE_RETURN") echo "任意のキーを押して戻る..." ;;
                "INVALID_INPUT") echo "入力が無効です。再入力してください。" ;;
                "SERVER_PROMPT") echo "サーバーを選択してください (CN/JP/GL): " ;;
                "MODE_PROMPT") echo "モードを選択してください (Extract / Repack): " ;;
                "TABLE_FOLDER_PROMPT") echo "ExcelDB.db と Excel.zip があるディレクトリを入力してください: " ;;
                "TABLE_FOLDER_ERR") echo "警告：このディレクトリに ExcelDB.db または Excel.zip が見つかりません！" ;;
                "OUT_JSON_PROMPT") echo "出力先 JSON ディレクトリを入力してください: " ;;
                "IN_JSON_PROMPT") echo "パックする JSON ディレクトリを入力してください (内に Excel/ExcelDB フォルダが必要): " ;;
                "IN_JSON_ERR") echo "警告：対象ディレクトリには 'Excel' または 'ExcelDB' サブフォルダが含まれている必要があります！" ;;
                "DB_KEY_PROMPT") echo "DB キーを入力してください (不要な場合は空欄): " ;;
                "CATALOG_PROMPT") echo "TableCatalog を変更しますか？ (y/n): " ;;
                "NAME_PROMPT") echo "ファイル名を難読化しますか？ (y/n): " ;;
                "PY_NOT_FOUND") echo "Python が検出されませんでした。自動インストールを試みます..." ;;
                "SCRIPT_NOT_FOUND") echo "エラー: スクリプト %s が見つかりません！" ;;
                "GET_CATALOG") echo "Catalog を取得" ;;
                "GET_FILES") echo "ファイルをダウンロード" ;;
                "GET_VERSION") echo "現在のバージョンを取得" ;;
                "UPDATE_ENV") echo "env 設定を更新" ;;
                "TYPE_PROMPT") echo "リソースタイプを選択 (Table/Media/Bundle): " ;;
                "CLIENT_PROMPT") echo "クライアントプラットフォームを選択 (Android/iOS/Windows): " ;;
                "FILES_PROMPT") echo "ダウンロードするファイル名の一覧を入力 (カンマ区切り、例: ExcelDB.db,Excel.zip): " ;;
                "IS_FULL_VERSION") echo "マイナーバージョン番号を含めますか？ (y/n): " ;;
                "VERSION_KEY_PROMPT") echo "特定のバージョン キーを選択 (TableVersion/MediaVersion/PatchVersion/ResourceVersion): " ;;
                "FLATDATA_BRANCH_PROMPT") echo "FlatData のブランチ地域を選択 (CN/GL/JP): " ;;
                "DEP_OPT_1") echo "Gitサブモジュールのチェック/同期 (crcmanip, PyCriCodecs)" ;;
                "DEP_OPT_2") echo "requirements.txtの不足しているpipライブラリのチェックとインストール" ;;
                "DEP_OPT_3") echo "sqlcipher環境のインストールと設定" ;;
                "DEP_OPT_4") echo "BAJpApkSrcのクローン" ;;
                "DEP_OPT_5") echo "BA-FlatDataのクローン" ;;
                "DEP_OPT_ALL") echo "すべての依存関係を一括インストール" ;;
                "SUBMODULE_START") echo "Git サブモジュールのチェックと同期を開始します..." ;;
                "SUBMODULE_DONE") echo "サブモジュールの処理が完了しました。" ;;
                "REQ_START") echo "requirements.txt の不足している依存関係の分析とインストールを開始します..." ;;
                "REQ_MISSING") echo "不足しているライブラリを個別にインストールしています: %s" ;;
                "REQ_ALL_INSTALLED") echo "requirements.txt 内のすべてのライブラリはすでにインストールされています。" ;;
                "REQ_NOT_FOUND") echo "requirements.txt ファイルが見つかりません！" ;;
                "SQLCIPHER_START") echo "sqlcipher のビルド環境の設定を開始します..." ;;
                "SQLCIPHER_PIP") echo "pysqlcipher3 をインストールしています..." ;;
                "SQLCIPHER_DONE") echo "sqlcipher コンポーネントの設定が完了しました。" ;;
                "FLATDATA_START") echo "BA-FlatData リポジトリの %s ブランチをクローンしています..." ;;
                "FLATDATA_DONE") echo "FlatData のクローンが完了しました。" ;;
            esac
            ;;
        "VN")
            case $key in
                "TITLE") echo "Kịch Bản Điều Khiển Chính" ;;
                "CHECKING") echo "Đang kiểm tra môi trường..." ;;
                "MISSING") echo "Phát hiện thiếu các phụ thuộc sau:" ;;
                "INSTALLING") echo "Đang xử lý cài đặt, vui lòng đợi..." ;;
                "EXIT") echo "Thoát Kịch Bản" ;;
                "BACK") echo "Quay Lại Menu Trước" ;;
                "SUB_MAIN") echo "Menu Chức Năng Chính" ;;
                "ASSIST") echo "Menu Chức Năng Phụ Trợ" ;;
                "DEP_MENU") echo "Menu Cài Đặt Phụ Thuộc" ;;
                "LANG_SET") echo "Cài Đặt Ngôn Ngữ" ;;
                "PACK_APK") echo "Đóng Gói APK" ;;
                "PROCESS_EXCEL") echo "Xử Lý ExcelDB.db Và Excel.zip" ;;
                "SDK_PROMPT") echo "Nhập SDKURL (Để trống để bỏ qua): " ;;
                "CFG_PROMPT") echo "Sửa đổi GameMainConfig? (y/n): " ;;
                "FIELDS_PROMPT") echo "Nhập tên các trường (phân tách bằng dấu phẩy): " ;;
                "VALUE_PROMPT") echo "Nhập giá trị cho %s: " ;;
                "COEXIST_PROMPT") echo "Sử dụng gói chạy song song? (y/n): " ;;
                "TRUST_PROMPT") echo "Tin tưởng chứng chỉ CA? (y/n): " ;;
                "LOGIN_PROMPT") echo "Đổi văn bản đăng nhập thành tiếng Trung? (y/n): " ;;
                "CLONING") echo "Đang sao chép từ GitHub..." ;;
                "RUNNING_CMD") echo "Thực thi lệnh: %s" ;;
                "DONE_RETURN") echo "Nhấn phím bất kỳ để quay lại..." ;;
                "INVALID_INPUT") echo "Dữ liệu nhập không hợp lệ, vui lòng thử lại." ;;
                "SERVER_PROMPT") echo "Vui lòng chọn máy chủ (CN/JP/GL): " ;;
                "MODE_PROMPT") echo "Vui lòng chọn chế độ (Extract / Repack): " ;;
                "TABLE_FOLDER_PROMPT") echo "Nhập thư mục chứa ExcelDB.db và Excel.zip: " ;;
                "TABLE_FOLDER_ERR") echo "Cảnh báo: Không tìm thấy ExcelDB.db hoặc Excel.zip trong thư mục này!" ;;
                "OUT_JSON_PROMPT") echo "Nhập thư mục xuất JSON: " ;;
                "IN_JSON_PROMPT") echo "Nhập thư mục JSON cần đóng gói (phải chứa thư mục con Excel/ExcelDB): " ;;
                "IN_JSON_ERR") echo "Cảnh báo: Thư mục mục tiêu phải chứa các thư mục con 'Excel' hoặc 'ExcelDB'!" ;;
                "DB_KEY_PROMPT") echo "Nhập DB Key (để trống nếu không cần): " ;;
                "CATALOG_PROMPT") echo "Sửa đổi TableCatalog? (y/n): " ;;
                "NAME_PROMPT") echo "Xáo trộn tên tệp? (y/n): " ;;
                "PY_NOT_FOUND") echo "Không tìm thấy Python, đang thử tự động cài đặt..." ;;
                "SCRIPT_NOT_FOUND") echo "Lỗi: Không tìm thấy kịch bản %s!" ;;
                "GET_CATALOG") echo "Tải Catalog" ;;
                "GET_FILES") echo "Tải Xuống Tệp Tin" ;;
                "GET_VERSION") echo "Lấy Số Phiên Bản Hiện Tại" ;;
                "UPDATE_ENV") echo "Cập Nhật Cấu Hình Env" ;;
                "TYPE_PROMPT") echo "Chọn loại tài nguyên (Table/Media/Bundle): " ;;
                "CLIENT_PROMPT") echo "Chọn nền tảng ứng dụng (Android/iOS/Windows): " ;;
                "FILES_PROMPT") echo "Nhập danh sách tệp cần tải (phân tách bằng dấu phẩy, vd: ExcelDB.db,Excel.zip): " ;;
                "IS_FULL_VERSION") echo "Bao gồm số phiên bản phụ? (y/n): " ;;
                "VERSION_KEY_PROMPT") echo "Chọn mã khóa phiên bản cụ thể (TableVersion/MediaVersion/PatchVersion/ResourceVersion): " ;;
                "FLATDATA_BRANCH_PROMPT") echo "Chọn phân vùng nhánh FlatData (CN/GL/JP): " ;;
                "DEP_OPT_1") echo "Kiểm tra/Đồng bộ Git Submodules (crcmanip, PyCriCodecs)" ;;
                "DEP_OPT_2") echo "Kiểm tra & Cài đặt thư viện pip thiếu từ requirements.txt" ;;
                "DEP_OPT_3") echo "Cài đặt và cấu hình sqlcipher" ;;
                "DEP_OPT_4") echo "Bản sao BAJpApkSrc" ;;
                "DEP_OPT_5") echo "Bản sao BA-FlatData" ;;
                "DEP_OPT_ALL") echo "Cài đặt tất cả phụ thuộc bằng một cú nhấp" ;;
                "SUBMODULE_START") echo "Bắt đầu kiểm tra và đồng bộ Git submodules..." ;;
                "SUBMODULE_DONE") echo "Xử lý submodules hoàn tất." ;;
                "REQ_START") echo "Bắt đầu phân tích và cài đặt bổ sung các phụ thuộc thiếu từ requirements.txt..." ;;
                "REQ_MISSING") echo "Đang cài đặt riêng lẻ thư viện bị thiếu: %s" ;;
                "REQ_ALL_INSTALLED") echo "Tất cả các thư viện trong requirements.txt đã được cài đặt." ;;
                "REQ_NOT_FOUND") echo "Không tìm thấy tệp requirements.txt!" ;;
                "SQLCIPHER_START") echo "Bắt đầu cấu hình môi trường biên dịch sqlcipher..." ;;
                "SQLCIPHER_PIP") echo "Đang cài đặt pysqlcipher3..." ;;
                "SQLCIPHER_DONE") echo "Cấu hình các thành phần sqlcipher hoàn tất." ;;
                "FLATDATA_START") echo "Đang sao chép nhánh %s của kho lưu trữ BA-FlatData..." ;;
                "FLATDATA_DONE") echo "Hoàn tất sao chép FlatData." ;;
            esac
            ;;
    esac
}


draw_header() {
    clear
    echo -e "${C_ACCENT}╭────────────────────────────────────────────────────╮${C_DEF}" >&2
    echo -e "${C_ACCENT}│${C_DEF}  ${C_TITLE}$1${C_DEF}" >&2
    echo -e "${C_ACCENT}├────────────────────────────────────────────────────┤${C_DEF}" >&2
}

draw_option() {
    echo -e "${C_ACCENT}│${C_DEF}  ${C_OK}$1.${C_DEF} $2" >&2
}

draw_footer() {
    echo -e "${C_ACCENT}╰────────────────────────────────────────────────────╯${C_DEF}" >&2
    echo -en "${C_WARN}>> ${C_DEF}" >&2
}

print_info() {
    echo -e "${C_ACCENT}[*]${C_DEF} $1" >&2
}

print_input() {
    echo -en "${C_WARN}[?]${C_DEF} $1" >&2
}

get_valid_input() {
    local prompt=$1
    local regex=$2
    local input
    while true; do
        [[ -n "$prompt" ]] && print_input "$prompt"
        read -r input
        if [[ $input =~ $regex ]]; then
            echo "$input"
            return
        fi
        echo -e "${C_ERR}$(get_text INVALID_INPUT)${C_DEF}" >&2
    done
}

# 检查是否存在python
check_python_env() {
    if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
        print_info "$(get_text PY_NOT_FOUND)"
        sudo apt-get update && sudo apt-get install python3 python3-pip -y
    fi
}

# 依赖5 检查BAJpApkSrc是否存在
func_check_src_folder() {
    if [ ! -d "BAJpApkSrc" ]; then
        print_info "$(get_text CLONING)"
        git clone https://github.com/beichen23333/BAJpApkSrc
    fi
    return 0
}

# 主功能1 修改apk
func_pack_apk() {
    func_check_src_folder || return 1
    
    echo -e "\n${C_ACCENT}─── $(get_text PACK_APK) ───${C_DEF}"
    print_input "$(get_text SDK_PROMPT)"; read -r sdk_url
    
    local mod_cfg=$(get_valid_input "$(get_text CFG_PROMPT)" "^[YyNn]$")
    local json_str="{}"
    
    if [[ "$mod_cfg" =~ [Yy] ]]; then
        print_input "$(get_text FIELDS_PROMPT)"; read -r fields
        IFS=',' read -ra ADDR <<< "$fields"
        json_str="{"
        for i in "${!ADDR[@]}"; do
            field=$(echo "${ADDR[$i]}" | xargs)
            printf "${C_WARN}[?]${C_DEF} $(get_text VALUE_PROMPT)" "$field"
            read -r val
            json_str+="\"$field\": \"$val\""
            [[ $i -lt $((${#ADDR[@]} - 1)) ]] && json_str+=", "
        done
        json_str+="}"
    fi

    local use_coexist=$(get_valid_input "$(get_text COEXIST_PROMPT)" "^[YyNn]$")
    local use_trust=$(get_valid_input "$(get_text TRUST_PROMPT)" "^[YyNn]$")
    local mod_login=$(get_valid_input "$(get_text LOGIN_PROMPT)" "^[YyNn]$")

    local cmd="python -m update.update_apk"
    [[ -n "$sdk_url" ]] && cmd+=" --sdkurl $sdk_url"
    [[ "$mod_cfg" =~ [Yy] ]] && cmd+=" --gamemainconfig '$json_str'"
    [[ "$use_coexist" =~ [Yy] ]] && cmd+=" --coexist"
    [[ "$use_trust" =~ [Yy] ]] && cmd+=" --trustcert"
    [[ "$mod_login" =~ [Yy] ]] && cmd+=" --modifylogin"

    echo ""
    printf "${C_OK}[✓]${C_DEF} $(get_text RUNNING_CMD)\n" "${C_TITLE}$cmd${C_DEF}"
    eval $cmd
}

# 主功能2 处理ExcelDB或Excel
func_process_excel() {
    local target_script="process_excel.py"
    if [ ! -f "$target_script" ]; then
        printf "${C_ERR}$(get_text SCRIPT_NOT_FOUND)${C_DEF}\n" "$target_script"
        sleep 2
        return 1
    fi

    echo -e "\n${C_ACCENT}─── $(get_text PROCESS_EXCEL) ───${C_DEF}"
    
    local raw_server=$(get_valid_input "$(get_text SERVER_PROMPT)" "^([Cc][Nn]|[Jj][Pp]|[Gg][Ll])$")
    local server="${raw_server^^}"

    local raw_mode=$(get_valid_input "$(get_text MODE_PROMPT)" "^([Ee][Xx][Tt][Rr][Aa][Cc][Tt]|[Rr][Ee][Pp][Aa][Cc][Kk])$")
    local mode="Extract"
    [[ "${raw_mode,,}" == "repack" ]] && mode="Repack"

    local table_file_folder
    while true; do
        print_input "$(get_text TABLE_FOLDER_PROMPT)"
        read -r table_file_folder
        if [ -d "$table_file_folder" ]; then
            if [ -f "$table_file_folder/ExcelDB.db" ] || [ -f "$table_file_folder/Excel.zip" ]; then
                break
            else
                echo -e "${C_ERR}$(get_text TABLE_FOLDER_ERR)${C_DEF}"
            fi
        else
            echo -e "${C_ERR}$(get_text INVALID_INPUT)${C_DEF}"
        fi
    done

    local file_path
    while true; do
        if [ "$mode" == "Extract" ]; then
            print_input "$(get_text OUT_JSON_PROMPT)"
        else
            print_input "$(get_text IN_JSON_PROMPT)"
        fi
        read -r file_path
        
        if [ "$mode" == "Repack" ]; then
            if [ ! -d "$file_path/Excel" ] && [ ! -d "$file_path/ExcelDB" ]; then
                echo -e "${C_ERR}$(get_text IN_JSON_ERR)${C_DEF}"
                continue
            fi
        fi
        break
    done

    print_input "$(get_text DB_KEY_PROMPT)"; read -r db_key
    local catalog=$(get_valid_input "$(get_text CATALOG_PROMPT)" "^[YyNn]$")
    local name=$(get_valid_input "$(get_text NAME_PROMPT)" "^[YyNn]$")

    local cmd="python $target_script '$table_file_folder' '$file_path' $server $mode"
    [[ -n "$db_key" ]] && cmd+=" --db_key '$db_key'"
    [[ "$catalog" =~ [Yy] ]] && cmd+=" --catalog"
    [[ "$name" =~ [Yy] ]] && cmd+=" --name"

    echo ""
    printf "${C_OK}[✓]${C_DEF} $(get_text RUNNING_CMD)\n" "${C_TITLE}$cmd${C_DEF}"
    eval $cmd
}

# 辅助功能1 获取catalog
func_assist_get_catalog() {
    echo -e "\n${C_ACCENT}─── $(get_text GET_CATALOG) ───${C_DEF}"
    check_python_env
    local raw_server=$(get_valid_input "$(get_text SERVER_PROMPT)" "^([Cc][Nn]|[Jj][Pp]|[Gg][Ll])$")
    local server="${raw_server^^}"
    
    local raw_type=$(get_valid_input "$(get_text TYPE_PROMPT)" "^([Mm][Ee][Dd][Ii][Aa]|[Tt][Aa][Bb][Ll][Ee]|[Bb][Uu][Nnd][Dd][Ll][Ee])$")
    local res_type="${raw_type,,}"
    res_type="${res_type^}"
    
    local raw_client=$(get_valid_input "$(get_text CLIENT_PROMPT)" "^([Aa][Nn][Dd][Rr][Oo][Ii][Dd]|[Ii][Oo][Ss]|[Ww][Ii][Nn][Dd][Oo][Ww][Ss])$")
    local client="${raw_client,,}"
    [[ "$client" == "ios" ]] && client="iOS" || client="${client^}"

    local cmd="python -m get.get_catalog $server $res_type $client"
    echo ""
    printf "${C_OK}[✓]${C_DEF} $(get_text RUNNING_CMD)\n" "${C_TITLE}$cmd${C_DEF}"
    eval $cmd
}

# 辅助功能2 获取文件
func_assist_get_files() {
    echo -e "\n${C_ACCENT}─── $(get_text GET_FILES) ───${C_DEF}"
    check_python_env
    local raw_server=$(get_valid_input "$(get_text SERVER_PROMPT)" "^([Cc][Nn]|[Jj][Pp]|[Gg][Ll])$")
    local server="${raw_server^^}"
    
    local raw_type=$(get_valid_input "$(get_text TYPE_PROMPT)" "^([Mm][Ee][Dd][Ii][Aa]|[Tt][Aa][Bb][Ll][Ee]|[Bb][Uu][Nnd][Dd][Ll][Ee])$")
    local res_type="${raw_type,,}"
    res_type="${res_type^}"
    
    local raw_client=$(get_valid_input "$(get_text CLIENT_PROMPT)" "^([Aa][Nn][Dd][Rr][Oo][Ii][Dd]|[Ii][Oo][Ss]|[Ww][Ii][Nn][Dd][Oo][Ww][Ss])$")
    local client="${raw_client,,}"
    [[ "$client" == "ios" ]] && client="iOS" || client="${client^}"

    print_input "$(get_text FILES_PROMPT)"; read -r user_files
    
    local file_args=""
    if [[ -n "$user_files" ]]; then
        file_args="-f $(echo "$user_files" | sed "s/,/' '/g" | sed "s/^/'/" | sed "s/$/'/")"
    fi

    local cmd="python -m get.get_files $server $res_type $client $file_args"
    echo ""
    printf "${C_OK}[✓]${C_DEF} $(get_text RUNNING_CMD)\n" "${C_TITLE}$cmd${C_DEF}"
    eval $cmd
}

#辅助功能3 获取版本号
func_assist_get_version() {
    local target_script="get/get_version.sh"
    if [ ! -f "$target_script" ]; then
        printf "${C_ERR}$(get_text SCRIPT_NOT_FOUND)${C_DEF}\n" "$target_script"
        sleep 2
        return 1
    fi

    echo -e "\n${C_ACCENT}─── $(get_text GET_VERSION) ───${C_DEF}"
    
    local raw_server=$(get_valid_input "$(get_text SERVER_PROMPT)" "^([Cc][Nn]|[Jj][Pp]|[Gg][Ll])$")
    local server="${raw_server^^}"
    
    local raw_full=$(get_valid_input "$(get_text IS_FULL_VERSION)" "^[YyNn]$")
    local is_full_name="false"
    [[ "$raw_full" =~ [Yy] ]] && is_full_name="true"
    
    local target_version_key=""
    if [[ "$server" == "CN" && "$is_full_name" == "true" ]]; then
        target_version_key=$(get_valid_input "$(get_text VERSION_KEY_PROMPT)" "^([Tt][Aa][Bb][Ll][Ee][Vv][Ee][Rr][Ss][Ii][Oo][Nn]|[Mm][Ee][Dd][Ii][Aa][Vv][Ee][Rr][Ss][Ii][Oo][Nn]|[Pp][Aa][Tt][Cc][Hh][Vv][Ee][Rr][Ss][Ii][Oo][Nn]|[Rr][Ee][Ss][Oo][Uu][Rr][Cc][Ee][Vv][Ee][Rr][Ss][Ii][Oo][Nn])$")
        [[ "${target_version_key,,}" == "tableversion" ]] && target_version_key="TableVersion"
        [[ "${target_version_key,,}" == "mediaversion" ]] && target_version_key="MediaVersion"
        [[ "${target_version_key,,}" == "patchversion" ]] && target_version_key="PatchVersion"
        [[ "${target_version_key,,}" == "resourceversion" ]] && target_version_key="ResourceVersion"
    fi

    local cmd="bash $target_script $server $is_full_name $target_version_key"
    echo ""
    printf "${C_OK}[✓]${C_DEF} $(get_text RUNNING_CMD)\n" "${C_TITLE}$cmd${C_DEF}"
    eval $cmd
}

# 辅助功能4 更新Env
func_assist_update_env() {
    echo -e "\n${C_ACCENT}─── $(get_text UPDATE_ENV) ───${C_DEF}"
    check_python_env
    local raw_server=$(get_valid_input "$(get_text SERVER_PROMPT)" "^([Cc][Nn]|[Jj][Pp]|[Gg][Ll])$")
    local server="${raw_server^^}"

    local cmd="python -m update.update $server"
    echo ""
    printf "${C_OK}[✓]${C_DEF} $(get_text RUNNING_CMD)\n" "${C_TITLE}$cmd${C_DEF}"
    eval $cmd
}

# 依赖1 检查子模块
func_dep_check_submodules() {
    print_info "$(get_text SUBMODULE_START)"
    git submodule init && git submodule update --recursive
    print_info "$(get_text SUBMODULE_DONE)"
}

# 依赖2 检查requirements
func_dep_check_requirements() {
    check_python_env
    print_info "$(get_text REQ_START)"
    if [ -f "requirements.txt" ]; then
        local installed_pip
        installed_pip=$(python -m pip list --format=freeze 2>/dev/null | cut -d'=' -f1 | tr 'A-Z-' 'a-z_')
        local missing_pips=()
        
        while IFS= read -r pkg || [[ -n "$pkg" ]]; do
            [[ "$pkg" =~ ^#.* || -z "$pkg" || "$pkg" == *"./"* ]] && continue
            local req_pkg_name=$(echo "$pkg" | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1 | xargs)
            local norm_pkg_name=$(echo "$req_pkg_name" | tr 'A-Z-' 'a-z_')
            
            if ! echo "$installed_pip" | grep -Fqx "$norm_pkg_name" >/dev/null 2>&1; then
                missing_pips+=("$req_pkg_name")
            fi
        done < requirements.txt

        if [ ${#missing_pips[@]} -gt 0 ]; then
            printf "${C_ACCENT}[*]${C_DEF} $(get_text REQ_MISSING)\n" "${missing_pips[*]}"
            pip install "${missing_pips[@]}"
        else
            print_info "$(get_text REQ_ALL_INSTALLED)"
        fi
    else
        echo -e "${C_ERR}$(get_text REQ_NOT_FOUND)${C_DEF}"
    fi
}

# 依赖3 检查sqlcipher
func_dep_check_sqlcipher() {
    check_python_env
    print_info "$(get_text SQLCIPHER_START)"
    sudo apt-get update && sudo apt-get install -y sqlcipher libsqlcipher-dev
    print_info "$(get_text SQLCIPHER_PIP)"
    pip install pysqlcipher3
    print_info "$(get_text SQLCIPHER_DONE)"
}

# 依赖4 克隆flatdata
func_dep_clone_flatdata() {
    local raw_branch=$(get_valid_input "$(get_text FLATDATA_BRANCH_PROMPT)" "^([Cc][Nn]|[Gg][Ll]|[Jj][Pp])$")
    local branch="${raw_branch^^}"
    
    printf "${C_ACCENT}[*]${C_DEF} $(get_text FLATDATA_START)\n" "$branch"
    git clone -b "$branch" --single-branch https://github.com/beichen23333/BA-FlatData.git FlatData
    print_info "$(get_text FLATDATA_DONE)"
}

# 依赖6 执行全部
func_dep_all_install() {
    func_dep_check_submodules
    func_dep_check_requirements
    func_dep_check_sqlcipher
    func_check_src_folder
    func_dep_clone_flatdata
}

# 语言设置
func_set_language() {
    draw_header "$(get_text LANG_SET)"
    draw_option 1 "简体中文"
    draw_option 2 "English"
    draw_option 3 "日本語"
    draw_option 4 "Tiếng Việt"
    draw_option 0 "$(get_text BACK)"
    draw_footer
    
    local lang_choice
    lang_choice=$(get_valid_input "" "^[01234]$")
    case $lang_choice in
        1) LANG_TYPE="CN" ;;
        2) LANG_TYPE="EN" ;;
        3) LANG_TYPE="JP" ;;
        4) LANG_TYPE="VN" ;;
        0) break ;;
    esac
    echo "$LANG_TYPE" > "$CONFIG_FILE"
}

# 依赖菜单
func_submenu_dependencies() {
    while true; do
        draw_header "$(get_text DEP_MENU)"
        draw_option 1 "$(get_text DEP_OPT_1)"
        draw_option 2 "$(get_text DEP_OPT_2)"
        draw_option 3 "$(get_text DEP_OPT_3)"
        draw_option 4 "$(get_text DEP_OPT_4)"
        draw_option 5 "$(get_text DEP_OPT_5)"
        draw_option 6 "$(get_text DEP_OPT_ALL)"
        draw_option 0 "$(get_text BACK)"
        draw_footer
        
        local dep_choice
        dep_choice=$(get_valid_input "" "^[0123456]$")
        case $dep_choice in
            1) func_dep_check_submodules ;;
            2) func_dep_check_requirements ;;
            3) func_dep_check_sqlcipher ;;
            4) func_check_src_folder ;;
            5) func_dep_clone_flatdata ;;
            6) func_dep_all_install ;;
            0) break ;;
        esac
        echo -en "\n${C_WARN}$(get_text DONE_RETURN)${C_DEF}"
        read -n 1 -s -r 
    done
}

# 主功能菜单
func_submenu_main() {
    while true; do
        draw_header "$(get_text SUB_MAIN)"
        draw_option 1 "$(get_text PACK_APK)"
        draw_option 2 "$(get_text PROCESS_EXCEL)"
        draw_option 0 "$(get_text BACK)"
        draw_footer
        
        local sub_choice
        sub_choice=$(get_valid_input "" "^[012]$")
        case $sub_choice in
            1) 
                func_pack_apk
                echo -en "\n${C_WARN}$(get_text DONE_RETURN)${C_DEF}"
                read -n 1 -s -r 
                ;;
            2)
                func_process_excel
                echo -en "\n${C_WARN}$(get_text DONE_RETURN)${C_DEF}"
                read -n 1 -s -r 
                ;;
            0) break ;;
        esac
    done
}

# 辅助菜单
func_submenu_assist() {
    while true; do
        draw_header "$(get_text ASSIST)"
        draw_option 1 "$(get_text GET_CATALOG)"
        draw_option 2 "$(get_text GET_FILES)"
        draw_option 3 "$(get_text GET_VERSION)"
        draw_option 4 "$(get_text UPDATE_ENV)"
        draw_option 0 "$(get_text BACK)"
        draw_footer
        
        local assist_choice
        assist_choice=$(get_valid_input "" "^[01234]$")
        case $assist_choice in
            1) func_assist_get_catalog ;;
            2) func_assist_get_files ;;
            3) func_assist_get_version ;;
            4) func_assist_update_env ;;
            0) break ;;
        esac
        echo -en "\n${C_WARN}$(get_text DONE_RETURN)${C_DEF}"
        read -n 1 -s -r 
    done
}

# 主菜单
while true; do
    draw_header "$(get_text TITLE) [${LANG_TYPE}]"
    draw_option 1 "$(get_text DEP_MENU)"
    draw_option 2 "$(get_text SUB_MAIN)"
    draw_option 3 "$(get_text ASSIST)"
    draw_option 4 "$(get_text LANG_SET)"
    draw_option 0 "$(get_text EXIT)"
    draw_footer
    
    choice=$(get_valid_input "" "^[01234]$")
    case $choice in
        1) func_submenu_dependencies ;;
        2) func_submenu_main ;;
        3) func_submenu_assist ;;
        4) func_set_language ;;
        0) 
            clear
            exit 0 
            ;;
    esac
done
