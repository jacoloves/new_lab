# ワーカープロセスの数
# - メモリ使用量が搭載量を超えないように注意
# - CPUの処理のみであればコア数と同じに設定するが、
# 実際はDBのI/O待ちも発生するため、コア数の2倍程度が目安
worker_processes 8

# PID ファイルの場所
pid "/var/run/rails-app-unicorn.pid"

# リッスンするソケットの指定
# ここではUNIXドメインソケットを使用
listen "/var/run/rails-app-unicorn.sock"

# 標準出力、標準エラー出力のログファイル
stdout_path "./log/unicorn.stdout.log"
stderr_path "./log/unicorn.stderr.log"