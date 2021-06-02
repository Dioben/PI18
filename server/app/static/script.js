function string2color(str) {
    let hash = 0, i, chr;
    if (str.length === 0) return "black";
    let regex = / \([0-9]*\)$/g;
    if (str.match(regex)) str = str.replace(regex, "");
    for (i = 0; i < str.length; i++) {
        chr   = str.charCodeAt(i);
        hash  = ((hash << 5) - hash) + chr;
        hash |= 0;
    }
    return "hsl(" + Math.abs(hash) % 360 + ", 100%, 30%)";
}