最終的に[Gauche](http://practical-scheme.net/gauche/index-j.htmlk)を使用することにした。

VScodeでdevcontainerで開発する場合はプロンプトでgoshと打ち込むとREPLを起動する。

## REPLで立ち上げる場合
```
docker run -it --rm practicalscheme/gauche
```

## ファイルをマウントして実行したい
```
docker run --rm -v $(pwd):/usr/src/app -w /usr/src/app practicalscheme/gauche gauche youfile.scm
```
