let line:string = "";
for (let i:number = 1; i <= 9; i++) {
  for (let j:number = 1; j <= 9; j++) {
    line += i * j + "\t";
  }
  console.log(line);
  line = "";
}
