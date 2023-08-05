function mixer(x) {
  return x.join("と")+"ジュース";
}

let material: string[] = ["オレンジ", "パイナップル", "マンゴー", "ブドウ"];

const juice: string = mixer(material);
console.log(juice);
