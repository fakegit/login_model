var _keys = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
var _keys_urlsafe = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_=";
var _subp_v2_keys = "uAL715W8e3jJCcNU0lT_FSXVgxpbEDdQ4vKaIOH2GBPtfzqsmYZo-wRM9i6hynrk=";
var _subp_v3_keys_3 = "5WFh28sGziZTeS1lBxCK-HgPq9IdMUwknybo.LJrQD3uj_Va7pE0XfcNR4AOYvm6t";

function base64Encode(a) {
    a = "" + a;
    if (a == "")
        return "";
    var b = "", c, d, e = "", f, g, h, i = "", j = 0;
    do {
        c = a.charCodeAt(j++);
        d = a.charCodeAt(j++);
        e = a.charCodeAt(j++);
        f = c >> 2;
        g = (c & 3) << 4 | d >> 4;
        h = (d & 15) << 2 | e >> 6;
        i = e & 63;
        isNaN(d) ? h = i = 64 : isNaN(e) && (i = 64);
        b = b + _keys.charAt(f) + _keys.charAt(g) + _keys.charAt(h) + _keys.charAt(i);
        c = d = e = "";
        f = g = h = i = ""
    } while (j < a.length);return b
}

function urlencode(a) {
    return encodeURIComponent(a)
}

function getSu(userName) {
    return base64Encode(urlencode(userName))
}

// console.log(getSu('18829040039'));