var line = "";
for (var i = 1; i <= 9; i++) {
    for (var j = 1; j <= 9; j++) {
        line += i * j + "\t";
    }
    console.log(line);
    line = "";
}
