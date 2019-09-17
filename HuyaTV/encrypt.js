function hexEncode(d) {
    return toHex(core(toArray(d)))
}

function toArray(g) {
    var e = ((g.length + 8) >> 6) + 1
        , d = new Array(e * 16);
    for (var f = 0; f < e * 16; f++) {
        d[f] = 0
    }
    for (f = 0; f < g.length; f++) {
        d[f >> 2] |= g.charCodeAt(f) << (24 - (f & 3) * 8)
    }
    d[f >> 2] |= 128 << (24 - (f & 3) * 8);
    d[e * 16 - 1] = g.length * 8;
    return d
}

function toHex(d) {
    var g = "0123456789abcdef"
        , f = "";
    for (var e = 0; e < d.length * 4; e++) {
        f += g.charAt((d[e >> 2] >> ((3 - e % 4) * 8 + 4)) & 15) + g.charAt((d[e >> 2] >> ((3 - e % 4) * 8)) & 15)
    }
    return f
}

function core(y) {
    var f = y;
    var v = new Array(80);
    var u = 1732584193;
    var s = -271733879;
    var r = -1732584194;
    var q = 271733878;
    var p = -1009589776;
    for (var m = 0; m < f.length; m += 16) {
        var o = u;
        var n = s;
        var l = r;
        var k = q;
        var g = p;
        for (var h = 0; h < 80; h++) {
            if (h < 16) {
                v[h] = f[m + h]
            } else {
                v[h] = rol(v[h - 3] ^ v[h - 8] ^ v[h - 14] ^ v[h - 16], 1)
            }
            var x = add(add(rol(u, 5), ft(h, s, r, q)), add(add(p, v[h]), kt(h)));
            p = q;
            q = r;
            r = rol(s, 30);
            s = u;
            u = x
        }
        u = add(u, o);
        s = add(s, n);
        r = add(r, l);
        q = add(q, k);
        p = add(p, g)
    }
    return new Array(u, s, r, q, p)
}

function add(f, e) {
    var g = (f & 65535) + (e & 65535);
    var d = (f >> 16) + (e >> 16) + (g >> 16);
    return (d << 16) | (g & 65535)
}

function rol(d, e) {
    return (d << e) | (d >>> (32 - e))
}

function ft(f, e, h, g) {
    if (f < 20) {
        return (e & h) | ((~e) & g)
    } else {
        if (f < 40) {
            return e ^ h ^ g
        } else {
            if (f < 60) {
                return (e & h) | (e & g) | (h & g)
            }
        }
    }
    return e ^ h ^ g
}

function kt(d) {
    return (d < 20) ? 1518500249 : (d < 40) ? 1859775393 : (d < 60) ? -1894007588 : -899497514
}

//获取加密密码
function encryptPwd(pwd) {
    return hexEncode(pwd)
}


//获取随机requestId
function getRequestId(e) {
    var d = new Date();
    if (e && e == 1) {
        return (Date.UTC(d.getFullYear(), d.getMonth(), d.getDate(), d.getHours(), d.getMinutes(), d.getSeconds(), d.getMilliseconds()) - Date.UTC(d.getFullYear(), d.getMonth(), d.getDate(), 0, 0, 0, 0))
    } else {
        if (e && e == 2) {
            return Date.UTC(d.getFullYear(), d.getMonth(), d.getDate(), d.getHours(), d.getMinutes(), d.getSeconds(), d.getMilliseconds())
        } else {
            return "xxxxxxxxxxxx4xxxyxxxxxxxxxxxxxxx".replace(/[xy]/g, function (h) {
                var g = Math.random() * 16 | 0
                    , f = (h == "x") ? g : (g & 3 | 8);
                return f.toString(16)
            })
        }
    }
}

console.log(getRequestId(1))

//获取page
function getPage(url) {
    return encodeURIComponent(url)
}

// console.log(getPage('https://www.huya.com/l'));

function convert(e, d) {
    if (typeof e != "undefined" && (typeof e == "string" || typeof e == "boolean" || typeof e == "number")) {
        if (typeof e == "string") {
            return e.toString().replace(new RegExp('([""])', "g"), '\\"')
        } else {
            return e.toString()
        }
    } else {
        if (typeof d != "undefined") {
            return d
        } else {
            return ""
        }
    }
}


function get(d, cookie) {
    var h = d + "=";
    var f = cookie.split(";");
    for (var e = 0; e < f.length; e++) {
        var g = f[e];
        while (g.charAt(0) == " ") {
            g = g.substring(1, g.length)
        }
        if (g.indexOf(h) == 0) {
            return g.substring(h.length, g.length)
        }
    }
    return undefined
}

function getguid(cookie) {
    var reg = /udb_guiddata=((\w|-|\s)+)/ig;  // 正则表达式对象
    //cookie.replace(reg, function(s, value) {   // JS字符串替换
    //console.log(value)
    //})
    return reg.exec(cookie)[1]
}

//console.log(getguid('__yamid_tt1=0.1232795775887836; __yamid_new=C875D5606C80000176AD12EEAE0014D2; SoundValue=0.50; alphaValue=0.80; guid=3ad7b83861a9ea5c33512be62ce6b2fa; Hm_lvt_51700b6c722f5bb4cf39906a596ea41f=1558882650,1559909095,1559998946; __yasmid=0.1232795775887836; udb_passdata=3; isInLiveRoom=true; udb_guiddata=787b6ffa5e4c42a99091ab91d071ed2a; web_qrlogin_confirm_id=bf407b38-0a04-453a-8899-c93acf12f406; h_unt=1560003929; Hm_lpvt_51700b6c722f5bb4cf39906a596ea41f=1560003939; __yaoldyyuid=; _yasids=__rootsid%3DC87A02DEAC400001CC501DC016A81329; PHPSESSID=qdd0udkruqk8mi2u0unr4p53r5'))

function getContext(cookie) {
    return "WB-" + getguid(cookie) + "-" + convert(get("__yamid_new", cookie)) + "-" + convert(get("guid", cookie))
}

// console.log(getContext('__yamid_tt1=0.1232795775887836; __yamid_new=C875D5606C80000176AD12EEAE0014D2; SoundValue=0.50; alphaValue=0.80; guid=3ad7b83861a9ea5c33512be62ce6b2fa; Hm_lvt_51700b6c722f5bb4cf39906a596ea41f=1558882650,1559909095,1559998946; __yasmid=0.1232795775887836; udb_passdata=3; isInLiveRoom=true; udb_guiddata=787b6ffa5e4c42a99091ab91d071ed2a; web_qrlogin_confirm_id=bf407b38-0a04-453a-8899-c93acf12f406; h_unt=1560003929; Hm_lpvt_51700b6c722f5bb4cf39906a596ea41f=1560003939; __yaoldyyuid=; _yasids=__rootsid%3DC87A02DEAC400001CC501DC016A81329; PHPSESSID=qdd0udkruqk8mi2u0unr4p53r5'));

function guid(e) {
    var d = new Date();
    if (e && e == 1) {
        return (Date.UTC(d.getFullYear(), d.getMonth(), d.getDate(), d.getHours(), d.getMinutes(), d.getSeconds(), d.getMilliseconds()) - Date.UTC(d.getFullYear(), d.getMonth(), d.getDate(), 0, 0, 0, 0))
    } else {
        if (e && e == 2) {
            return Date.UTC(d.getFullYear(), d.getMonth(), d.getDate(), d.getHours(), d.getMinutes(), d.getSeconds(), d.getMilliseconds())
        } else {
            return "xxxxxxxxxxxx4xxxyxxxxxxxxxxxxxxx".replace(/[xy]/g, function (h) {
                var g = Math.random() * 16 | 0
                    , f = (h == "x") ? g : (g & 3 | 8);
                return f.toString(16)
            })
        }
    }
}

function getSdid() {
    return guid(1)
}

// console.log(getSdid);


