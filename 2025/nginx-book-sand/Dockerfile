FROM ruby:3.3

# 必要パッケージのインストール
# - build-essential: gemのnative extensionビルド用
# - nodejs / npm: RailsのJS周り
# - git: bundleで必要になることがある
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
    build-essential \
    nodejs \
    npm \
    git \
    && rm -rf /var/lib/apt/lists/*

# yarnのインストール
RUN npm install -g yarn

# アプリケーションディレクトリの作成
WORKDIR /app

# Gemfileのコピーとbundle installの実行
COPY Gemfile Gemfile.lock ./
RUN bundle install

# アプリケーションコードのコピー
COPY . .

# ポート3000番を開放
EXPOSE 3000

# サーバー起動コマンド
CMD ["bundle", "exec", "rails", "server", "-b", "0.0.0.0"]