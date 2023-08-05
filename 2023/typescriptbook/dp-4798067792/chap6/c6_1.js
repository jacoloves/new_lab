function mixer(x) {
    return x.join("と") + "ジュース";
}
var material = ["オレンジ", "パイナップル", "マンゴー", "ブドウ"];
var juice = mixer(material);
console.log(juice);
