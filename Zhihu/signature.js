function i(e, t, n) {
    var r, o, i, a, s, c, u, l, y, b = 0, g = [], E = 0, w = !1, _ = [], T = [], O = !1, S = !1;
    if (r = (n = n || {}).encoding || "UTF8",
        y = n.numRounds || 1,
        i = v(t, r),
    y !== parseInt(y, 10) || 1 > y)
        throw Error("numRounds must a integer >= 1");
    if ("SHA-1" === e)
        s = 512,
            c = G,
            u = H,
            a = 160,
            l = function (e) {
                return e.slice()
            }
        ;
    else if (0 === e.lastIndexOf("SHA-", 0))
        if (c = function (t, n) {
            return V(t, n, e)
        }
            ,
            u = function (t, n, r, o) {
                var i, a;
                if ("SHA-224" === e || "SHA-256" === e)
                    i = 15 + (n + 65 >>> 9 << 4),
                        a = 16;
                else {
                    if ("SHA-384" !== e && "SHA-512" !== e)
                        throw Error("Unexpected error in SHA-2 implementation");
                    i = 31 + (n + 129 >>> 10 << 5),
                        a = 32
                }
                for (; t.length <= i;)
                    t.push(0);
                for (t[n >>> 5] |= 128 << 24 - n % 32,
                         n += r,
                         t[i] = 4294967295 & n,
                         t[i - 1] = n / 4294967296 | 0,
                         r = t.length,
                         n = 0; n < r; n += a)
                    o = V(t.slice(n, n + a), o, e);
                if ("SHA-224" === e)
                    t = [o[0], o[1], o[2], o[3], o[4], o[5], o[6]];
                else if ("SHA-256" === e)
                    t = o;
                else if ("SHA-384" === e)
                    t = [o[0].a, o[0].b, o[1].a, o[1].b, o[2].a, o[2].b, o[3].a, o[3].b, o[4].a, o[4].b, o[5].a, o[5].b];
                else {
                    if ("SHA-512" !== e)
                        throw Error("Unexpected error in SHA-2 implementation");
                    t = [o[0].a, o[0].b, o[1].a, o[1].b, o[2].a, o[2].b, o[3].a, o[3].b, o[4].a, o[4].b, o[5].a, o[5].b, o[6].a, o[6].b, o[7].a, o[7].b]
                }
                return t
            }
            ,
            l = function (e) {
                return e.slice()
            }
            ,
        "SHA-224" === e)
            s = 512,
                a = 224;
        else if ("SHA-256" === e)
            s = 512,
                a = 256;
        else if ("SHA-384" === e)
            s = 1024,
                a = 384;
        else {
            if ("SHA-512" !== e)
                throw Error("Chosen SHA variant is not supported");
            s = 1024,
                a = 512
        }
    else {
        if (0 !== e.lastIndexOf("SHA3-", 0) && 0 !== e.lastIndexOf("SHAKE", 0))
            throw Error("Chosen SHA variant is not supported");
        var C = 6;
        if (c = q,
            l = function (e) {
                var t, n = [];
                for (t = 0; 5 > t; t += 1)
                    n[t] = e[t].slice();
                return n
            }
            ,
        "SHA3-224" === e)
            s = 1152,
                a = 224;
        else if ("SHA3-256" === e)
            s = 1088,
                a = 256;
        else if ("SHA3-384" === e)
            s = 832,
                a = 384;
        else if ("SHA3-512" === e)
            s = 576,
                a = 512;
        else if ("SHAKE128" === e)
            s = 1344,
                a = -1,
                C = 31,
                S = !0;
        else {
            if ("SHAKE256" !== e)
                throw Error("Chosen SHA variant is not supported");
            s = 1088,
                a = -1,
                C = 31,
                S = !0
        }
        u = function (e, t, n, r, o) {
            var i, a = C, c = [], u = (n = s) >>> 5, l = 0, f = t >>> 5;
            for (i = 0; i < f && t >= n; i += u)
                r = q(e.slice(i, i + u), r),
                    t -= n;
            for (e = e.slice(i),
                     t %= n; e.length < u;)
                e.push(0);
            for (e[(i = t >>> 3) >> 2] ^= a << 24 - i % 4 * 8,
                     e[u - 1] ^= 128,
                     r = q(e, r); 32 * c.length < o && (e = r[l % 5][l / 5 | 0],
                c.push((255 & e.b) << 24 | (65280 & e.b) << 8 | (16711680 & e.b) >> 8 | e.b >>> 24),
                !(32 * c.length >= o));)
                c.push((255 & e.a) << 24 | (65280 & e.a) << 8 | (16711680 & e.a) >> 8 | e.a >>> 24),
                0 == 64 * (l += 1) % n && q(null, r);
            return c
        }
    }
    o = B(e),
        this.setHMACKey = function (t, n, i) {
            var l;
            if (!0 === w)
                throw Error("HMAC key already set");
            if (!0 === O)
                throw Error("Cannot set HMAC key after calling update");
            if (!0 === S)
                throw Error("SHAKE is not supported for HMAC");
            if (t = (n = v(n, r = (i || {}).encoding || "UTF8")(t)).binLen,
                n = n.value,
                i = (l = s >>> 3) / 4 - 1,
            l < t / 8) {
                for (n = u(n, t, 0, B(e), a); n.length <= i;)
                    n.push(0);
                n[i] &= 4294967040
            } else if (l > t / 8) {
                for (; n.length <= i;)
                    n.push(0);
                n[i] &= 4294967040
            }
            for (t = 0; t <= i; t += 1)
                _[t] = 909522486 ^ n[t],
                    T[t] = 1549556828 ^ n[t];
            o = c(_, o),
                b = s,
                w = !0
        }
        ,
        this.update = function (e) {
            var t, n, r, a = 0, u = s >>> 5;
            for (e = (t = i(e, g, E)).binLen,
                     n = t.value,
                     t = e >>> 5,
                     r = 0; r < t; r += u)
                a + s <= e && (o = c(n.slice(r, r + u), o),
                    a += s);
            b += a,
                g = n.slice(a >>> 5),
                E = e % s,
                O = !0
        }
        ,
        this.getHash = function (t, n) {
            var r, i, s, c;
            if (!0 === w)
                throw Error("Cannot call getHash after setting HMAC key");
            if (s = m(n),
            !0 === S) {
                if (-1 === s.shakeLen)
                    throw Error("shakeLen must be specified in options");
                a = s.shakeLen
            }
            switch (t) {
                case "HEX":
                    r = function (e) {
                        return f(e, a, s)
                    }
                    ;
                    break;
                case "B64":
                    r = function (e) {
                        return p(e, a, s)
                    }
                    ;
                    break;
                case "BYTES":
                    r = function (e) {
                        return d(e, a)
                    }
                    ;
                    break;
                case "ARRAYBUFFER":
                    try {
                        i = new ArrayBuffer(0)
                    } catch (e) {
                        throw Error("ARRAYBUFFER not supported by this environment")
                    }
                    r = function (e) {
                        return h(e, a)
                    }
                    ;
                    break;
                default:
                    throw Error("format must be HEX, B64, BYTES, or ARRAYBUFFER")
            }
            for (c = u(g.slice(), E, b, l(o), a),
                     i = 1; i < y; i += 1)
                !0 === S && 0 != a % 32 && (c[c.length - 1] &= 4294967040 << 24 - a % 32),
                    c = u(c, a, 0, B(e), a);
            return r(c)
        }
        ,
        this.getHMAC = function (t, n) {
            var r, i, v, y;
            if (!1 === w)
                throw Error("Cannot call getHMAC without first setting HMAC key");
            switch (v = m(n),
                t) {
                case "HEX":
                    r = function (e) {
                        return f(e, a, v)
                    }
                    ;
                    break;
                case "B64":
                    r = function (e) {
                        return p(e, a, v)
                    }
                    ;
                    break;
                case "BYTES":
                    r = function (e) {
                        return d(e, a)
                    }
                    ;
                    break;
                case "ARRAYBUFFER":
                    try {
                        r = new ArrayBuffer(0)
                    } catch (e) {
                        throw Error("ARRAYBUFFER not supported by this environment")
                    }
                    r = function (e) {
                        return h(e, a)
                    }
                    ;
                    break;
                default:
                    throw Error("outputFormat must be HEX, B64, BYTES, or ARRAYBUFFER")
            }
            return i = u(g.slice(), E, b, l(o), a),
                y = c(T, B(e)),
                r(y = u(i, a, s, y, a))
        }
}
function a(e, t) {
    this.a = e,
    this.b = t
}
function s(e, t, n) {
    var r, o, i, a, s, c = e.length;
    if (t = t || [0],
        s = (n = n || 0) >>> 3,
    0 != c % 2)
        throw Error("String of HEX type must be in byte increments");
    for (r = 0; r < c; r += 2) {
        if (o = parseInt(e.substr(r, 2), 16),
            isNaN(o))
            throw Error("String of HEX type contains invalid characters");
        for (i = (a = (r >>> 1) + s) >>> 2; t.length <= i;)
            t.push(0);
        t[i] |= o << 8 * (3 - a % 4)
    }
    return {
        value: t,
        binLen: 4 * c + n
    }
}
function c(e, t, n) {
    var r, o, i, a, s = [];
    s = t || [0];
    for (o = (n = n || 0) >>> 3,
             r = 0; r < e.length; r += 1)
        t = e.charCodeAt(r),
            i = (a = r + o) >>> 2,
        s.length <= i && s.push(0),
            s[i] |= t << 8 * (3 - a % 4);
    return {
        value: s,
        binLen: 8 * e.length + n
    }
}
function u(e, t, n) {
    var r, o, i, a, s, c, u = [], l = 0;
    u = t || [0];
    if (t = (n = n || 0) >>> 3,
    -1 === e.search(/^[a-zA-Z0-9=+\/]+$/))
        throw Error("Invalid character in base-64 string");
    if (o = e.indexOf("="),
        e = e.replace(/\=/g, ""),
    -1 !== o && o < e.length)
        throw Error("Invalid '=' found in base-64 string");
    for (o = 0; o < e.length; o += 4) {
        for (s = e.substr(o, 4),
                 i = a = 0; i < s.length; i += 1)
            a |= (r = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".indexOf(s[i])) << 18 - 6 * i;
        for (i = 0; i < s.length - 1; i += 1) {
            for (r = (c = l + t) >>> 2; u.length <= r;)
                u.push(0);
            u[r] |= (a >>> 16 - 8 * i & 255) << 8 * (3 - c % 4),
                l += 1
        }
    }
    return {
        value: u,
        binLen: 8 * l + n
    }
}
function l(e, t, n) {
    var r, o, i, a = [];
    a = t || [0];
    for (r = (n = n || 0) >>> 3,
             t = 0; t < e.byteLength; t += 1)
        o = (i = t + r) >>> 2,
        a.length <= o && a.push(0),
            a[o] |= e[t] << 8 * (3 - i % 4);
    return {
        value: a,
        binLen: 8 * e.byteLength + n
    }
}
function f(e, t, n) {
    var r, o, i = "";
    for (t /= 8,
             r = 0; r < t; r += 1)
        o = e[r >>> 2] >>> 8 * (3 - r % 4),
            i += "0123456789abcdef".charAt(o >>> 4 & 15) + "0123456789abcdef".charAt(15 & o);
    return n.outputUpper ? i.toUpperCase() : i
}
function p(e, t, n) {
    var r, o, i, a = "", s = t / 8;
    for (r = 0; r < s; r += 3)
        for (o = r + 1 < s ? e[r + 1 >>> 2] : 0,
                 i = r + 2 < s ? e[r + 2 >>> 2] : 0,
                 i = (e[r >>> 2] >>> 8 * (3 - r % 4) & 255) << 16 | (o >>> 8 * (3 - (r + 1) % 4) & 255) << 8 | i >>> 8 * (3 - (r + 2) % 4) & 255,
                 o = 0; 4 > o; o += 1)
            a += 8 * r + 6 * o <= t ? "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".charAt(i >>> 6 * (3 - o) & 63) : n.b64Pad;
    return a
}
function d(e, t) {
    var n, r, o = "", i = t / 8;
    for (n = 0; n < i; n += 1)
        r = e[n >>> 2] >>> 8 * (3 - n % 4) & 255,
            o += String.fromCharCode(r);
    return o
}
function h(e, t) {
    var n, r = t / 8, o = new ArrayBuffer(r);
    for (n = 0; n < r; n += 1)
        o[n] = e[n >>> 2] >>> 8 * (3 - n % 4) & 255;
    return o
}
function m(e) {
    var t = {
        outputUpper: !1,
        b64Pad: "=",
        shakeLen: -1
    };
    if (e = e || {},
        t.outputUpper = e.outputUpper || !1,
    !0 === e.hasOwnProperty("b64Pad") && (t.b64Pad = e.b64Pad),
    !0 === e.hasOwnProperty("shakeLen")) {
        if (0 != e.shakeLen % 8)
            throw Error("shakeLen must be a multiple of 8");
        t.shakeLen = e.shakeLen
    }
    if ("boolean" != typeof t.outputUpper)
        throw Error("Invalid outputUpper formatting option");
    if ("string" != typeof t.b64Pad)
        throw Error("Invalid b64Pad formatting option");
    return t
}
function v(e, t) {
    var n;
    switch (t) {
        case "UTF8":
        case "UTF16BE":
        case "UTF16LE":
            break;
        default:
            throw Error("encoding must be UTF8, UTF16BE, or UTF16LE")
    }
    switch (e) {
        case "HEX":
            n = s;
            break;
        case "TEXT":
            n = function (e, n, r) {
                var o, i, a, s, c, u = [], l = [], f = 0;
                u = n || [0];
                if (a = (n = r || 0) >>> 3,
                "UTF8" === t)
                    for (o = 0; o < e.length; o += 1)
                        for (l = [],
                                 128 > (r = e.charCodeAt(o)) ? l.push(r) : 2048 > r ? (l.push(192 | r >>> 6),
                                     l.push(128 | 63 & r)) : 55296 > r || 57344 <= r ? l.push(224 | r >>> 12, 128 | r >>> 6 & 63, 128 | 63 & r) : (o += 1,
                                     r = 65536 + ((1023 & r) << 10 | 1023 & e.charCodeAt(o)),
                                     l.push(240 | r >>> 18, 128 | r >>> 12 & 63, 128 | r >>> 6 & 63, 128 | 63 & r)),
                                 i = 0; i < l.length; i += 1) {
                            for (s = (c = f + a) >>> 2; u.length <= s;)
                                u.push(0);
                            u[s] |= l[i] << 8 * (3 - c % 4),
                                f += 1
                        }
                else if ("UTF16BE" === t || "UTF16LE" === t)
                    for (o = 0; o < e.length; o += 1) {
                        for (r = e.charCodeAt(o),
                             "UTF16LE" === t && (r = (i = 255 & r) << 8 | r >>> 8),
                                 s = (c = f + a) >>> 2; u.length <= s;)
                            u.push(0);
                        u[s] |= r << 8 * (2 - c % 4),
                            f += 2
                    }
                return {
                    value: u,
                    binLen: 8 * f + n
                }
            }
            ;
            break;
        case "B64":
            n = u;
            break;
        case "BYTES":
            n = c;
            break;
        case "ARRAYBUFFER":
            try {
                n = new ArrayBuffer(0)
            } catch (e) {
                throw Error("ARRAYBUFFER not supported by this environment")
            }
            n = l;
            break;
        default:
            throw Error("format must be HEX, TEXT, B64, BYTES, or ARRAYBUFFER")
    }
    return n
}
function y(e, t) {
    return e << t | e >>> 32 - t
}
function b(e, t) {
    return 32 < t ? (t -= 32,
    new a(e.b << t | e.a >>> 32 - t, e.a << t | e.b >>> 32 - t)) : 0 !== t ? new a(e.a << t | e.b >>> 32 - t, e.b << t | e.a >>> 32 - t) : e
}
function g(e, t) {
    return e >>> t | e << 32 - t
}
function E(e, t) {
    var n = null;
    n = new a(e.a, e.b);
    return 32 >= t ? new a(n.a >>> t | n.b << 32 - t & 4294967295, n.b >>> t | n.a << 32 - t & 4294967295) : new a(n.b >>> t - 32 | n.a << 64 - t & 4294967295, n.a >>> t - 32 | n.b << 64 - t & 4294967295)
}
function w(e, t) {
    return 32 >= t ? new a(e.a >>> t, e.b >>> t | e.a << 32 - t & 4294967295) : new a(0, e.a >>> t - 32)
}
function _(e, t, n) {
    return e & t ^ ~e & n
}
function T(e, t, n) {
    return new a(e.a & t.a ^ ~e.a & n.a, e.b & t.b ^ ~e.b & n.b)
}
function O(e, t, n) {
    return e & t ^ e & n ^ t & n
}
function S(e, t, n) {
    return new a(e.a & t.a ^ e.a & n.a ^ t.a & n.a, e.b & t.b ^ e.b & n.b ^ t.b & n.b)
}
function C(e) {
    return g(e, 2) ^ g(e, 13) ^ g(e, 22)
}
function A(e) {
    var t = E(e, 28)
        , n = E(e, 34);
    return e = E(e, 39),
        new a(t.a ^ n.a ^ e.a, t.b ^ n.b ^ e.b)
}
function x(e) {
    return g(e, 6) ^ g(e, 11) ^ g(e, 25)
}
function I(e) {
    var t = E(e, 14)
        , n = E(e, 18);
    return e = E(e, 41),
        new a(t.a ^ n.a ^ e.a, t.b ^ n.b ^ e.b)
}
function P(e) {
    return g(e, 7) ^ g(e, 18) ^ e >>> 3
}
function k(e) {
    var t = E(e, 1)
        , n = E(e, 8);
    return e = w(e, 7),
        new a(t.a ^ n.a ^ e.a, t.b ^ n.b ^ e.b)
}
function j(e) {
    return g(e, 17) ^ g(e, 19) ^ e >>> 10
}
function N(e) {
    var t = E(e, 19)
        , n = E(e, 61);
    return e = w(e, 6),
        new a(t.a ^ n.a ^ e.a, t.b ^ n.b ^ e.b)
}
function R(e, t) {
    var n = (65535 & e) + (65535 & t);
    return ((e >>> 16) + (t >>> 16) + (n >>> 16) & 65535) << 16 | 65535 & n
}
function M(e, t, n, r) {
    var o = (65535 & e) + (65535 & t) + (65535 & n) + (65535 & r);
    return ((e >>> 16) + (t >>> 16) + (n >>> 16) + (r >>> 16) + (o >>> 16) & 65535) << 16 | 65535 & o
}
function D(e, t, n, r, o) {
    var i = (65535 & e) + (65535 & t) + (65535 & n) + (65535 & r) + (65535 & o);
    return ((e >>> 16) + (t >>> 16) + (n >>> 16) + (r >>> 16) + (o >>> 16) + (i >>> 16) & 65535) << 16 | 65535 & i
}
function L(e, t) {
    var n, r, o;
    return n = (65535 & e.b) + (65535 & t.b),
        o = (65535 & (r = (e.b >>> 16) + (t.b >>> 16) + (n >>> 16))) << 16 | 65535 & n,
        n = (65535 & e.a) + (65535 & t.a) + (r >>> 16),
        new a((65535 & (r = (e.a >>> 16) + (t.a >>> 16) + (n >>> 16))) << 16 | 65535 & n, o)
}
function U(e, t, n, r) {
    var o, i, s;
    return o = (65535 & e.b) + (65535 & t.b) + (65535 & n.b) + (65535 & r.b),
        s = (65535 & (i = (e.b >>> 16) + (t.b >>> 16) + (n.b >>> 16) + (r.b >>> 16) + (o >>> 16))) << 16 | 65535 & o,
        o = (65535 & e.a) + (65535 & t.a) + (65535 & n.a) + (65535 & r.a) + (i >>> 16),
        new a((65535 & (i = (e.a >>> 16) + (t.a >>> 16) + (n.a >>> 16) + (r.a >>> 16) + (o >>> 16))) << 16 | 65535 & o, s)
}
function F(e, t, n, r, o) {
    var i, s, c;
    return i = (65535 & e.b) + (65535 & t.b) + (65535 & n.b) + (65535 & r.b) + (65535 & o.b),
        c = (65535 & (s = (e.b >>> 16) + (t.b >>> 16) + (n.b >>> 16) + (r.b >>> 16) + (o.b >>> 16) + (i >>> 16))) << 16 | 65535 & i,
        i = (65535 & e.a) + (65535 & t.a) + (65535 & n.a) + (65535 & r.a) + (65535 & o.a) + (s >>> 16),
        new a((65535 & (s = (e.a >>> 16) + (t.a >>> 16) + (n.a >>> 16) + (r.a >>> 16) + (o.a >>> 16) + (i >>> 16))) << 16 | 65535 & i, c)
}
function z(e) {
    var t, n = 0, r = 0;
    for (t = 0; t < arguments.length; t += 1)
        n ^= arguments[t].b,
            r ^= arguments[t].a;
    return new a(r, n)
}
function B(e) {
    var t, n = [];
    if ("SHA-1" === e)
        n = [1732584193, 4023233417, 2562383102, 271733878, 3285377520];
    else if (0 === e.lastIndexOf("SHA-", 0))
        switch (n = [3238371032, 914150663, 812702999, 4144912697, 4290775857, 1750603025, 1694076839, 3204075428],
            t = [1779033703, 3144134277, 1013904242, 2773480762, 1359893119, 2600822924, 528734635, 1541459225],
            e) {
            case "SHA-224":
                break;
            case "SHA-256":
                n = t;
                break;
            case "SHA-384":
                n = [new a(3418070365, n[0]), new a(1654270250, n[1]), new a(2438529370, n[2]), new a(355462360, n[3]), new a(1731405415, n[4]), new a(41048885895, n[5]), new a(3675008525, n[6]), new a(1203062813, n[7])];
                break;
            case "SHA-512":
                n = [new a(t[0], 4089235720), new a(t[1], 2227873595), new a(t[2], 4271175723), new a(t[3], 1595750129), new a(t[4], 2917565137), new a(t[5], 725511199), new a(t[6], 4215389547), new a(t[7], 327033209)];
                break;
            default:
                throw Error("Unknown SHA variant")
        }
    else {
        if (0 !== e.lastIndexOf("SHA3-", 0) && 0 !== e.lastIndexOf("SHAKE", 0))
            throw Error("No SHA variants supported");
        for (e = 0; 5 > e; e += 1)
            n[e] = [new a(0, 0), new a(0, 0), new a(0, 0), new a(0, 0), new a(0, 0)]
    }
    return n
}
function G(e, t) {
    var n, r, o, i, a, s, c, u = [];
    for (n = t[0],
             r = t[1],
             o = t[2],
             i = t[3],
             a = t[4],
             c = 0; 80 > c; c += 1)
        u[c] = 16 > c ? e[c] : y(u[c - 3] ^ u[c - 8] ^ u[c - 14] ^ u[c - 16], 1),
            s = 20 > c ? D(y(n, 5), r & o ^ ~r & i, a, 1518500249, u[c]) : 40 > c ? D(y(n, 5), r ^ o ^ i, a, 1859775393, u[c]) : 60 > c ? D(y(n, 5), O(r, o, i), a, 2400959708, u[c]) : D(y(n, 5), r ^ o ^ i, a, 3395469782, u[c]),
            a = i,
            i = o,
            o = y(r, 30),
            r = n,
            n = s;
    return t[0] = R(n, t[0]),
        t[1] = R(r, t[1]),
        t[2] = R(o, t[2]),
        t[3] = R(i, t[3]),
        t[4] = R(a, t[4]),
        t
}
function H(e, t, n, r) {
    var o;
    for (o = 15 + (t + 65 >>> 9 << 4); e.length <= o;)
        e.push(0);
    for (e[t >>> 5] |= 128 << 24 - t % 32,
             t += n,
             e[o] = 4294967295 & t,
             e[o - 1] = t / 4294967296 | 0,
             t = e.length,
             o = 0; o < t; o += 16)
        r = G(e.slice(o, o + 16), r);
    return r
}
function V(e, t, n) {
    var r, o, i, s, c, u, l, f, p, d, h, m, v, y, b, g, E, w, z, B, G, H, V, q = [];
    if ("SHA-224" === n || "SHA-256" === n)
        d = 64,
            m = 1,
            H = Number,
            v = R,
            y = M,
            b = D,
            g = P,
            E = j,
            w = C,
            z = x,
            G = O,
            B = _,
            V = W;
    else {
        if ("SHA-384" !== n && "SHA-512" !== n)
            throw Error("Unexpected error in SHA-2 implementation");
        d = 80,
            m = 2,
            H = a,
            v = L,
            y = U,
            b = F,
            g = k,
            E = N,
            w = A,
            z = I,
            G = S,
            B = T,
            V = Y
    }
    for (n = t[0],
             r = t[1],
             o = t[2],
             i = t[3],
             s = t[4],
             c = t[5],
             u = t[6],
             l = t[7],
             h = 0; h < d; h += 1)
        16 > h ? (p = h * m,
            f = e.length <= p ? 0 : e[p],
            p = e.length <= p + 1 ? 0 : e[p + 1],
            q[h] = new H(f, p)) : q[h] = y(E(q[h - 2]), q[h - 7], g(q[h - 15]), q[h - 16]),
            f = b(l, z(s), B(s, c, u), V[h], q[h]),
            p = v(w(n), G(n, r, o)),
            l = u,
            u = c,
            c = s,
            s = v(i, f),
            i = o,
            o = r,
            r = n,
            n = v(f, p);
    return t[0] = v(n, t[0]),
        t[1] = v(r, t[1]),
        t[2] = v(o, t[2]),
        t[3] = v(i, t[3]),
        t[4] = v(s, t[4]),
        t[5] = v(c, t[5]),
        t[6] = v(u, t[6]),
        t[7] = v(l, t[7]),
        t
}
function q(e, t) {
    var n, r, o, i, s = [], c = [];
    if (null !== e)
        for (r = 0; r < e.length; r += 2)
            t[(r >>> 1) % 5][(r >>> 1) / 5 | 0] = z(t[(r >>> 1) % 5][(r >>> 1) / 5 | 0], new a((255 & e[r + 1]) << 24 | (65280 & e[r + 1]) << 8 | (16711680 & e[r + 1]) >>> 8 | e[r + 1] >>> 24, (255 & e[r]) << 24 | (65280 & e[r]) << 8 | (16711680 & e[r]) >>> 8 | e[r] >>> 24));
    for (n = 0; 24 > n; n += 1) {
        for (i = B("SHA3-"),
                 r = 0; 5 > r; r += 1)
            s[r] = z(t[r][0], t[r][1], t[r][2], t[r][3], t[r][4]);
        for (r = 0; 5 > r; r += 1)
            c[r] = z(s[(r + 4) % 5], b(s[(r + 1) % 5], 1));
        for (r = 0; 5 > r; r += 1)
            for (o = 0; 5 > o; o += 1)
                t[r][o] = z(t[r][o], c[r]);
        for (r = 0; 5 > r; r += 1)
            for (o = 0; 5 > o; o += 1)
                i[o][(2 * r + 3 * o) % 5] = b(t[r][o], K[r][o]);
        for (r = 0; 5 > r; r += 1)
            for (o = 0; 5 > o; o += 1)
                t[r][o] = z(i[r][o], new a(~i[(r + 1) % 5][o].a & i[(r + 2) % 5][o].a, ~i[(r + 1) % 5][o].b & i[(r + 2) % 5][o].b));
        t[0][0] = z(t[0][0], Q[n])
    }
    return t
}
var W, Y, K, Q;
Y = [new a((W = [1116352408, 1899447441, 3049323471, 3921009573, 961987163, 1508970993, 2453635748, 2870763221, 3624381080, 310598401, 607225278, 1426881987, 1925078388, 2162078206, 2614888103, 3248222580, 3835390401, 4022224774, 264347078, 604807628, 770255983, 1249150122, 1555081692, 1996064986, 2554220882, 2821834349, 2952996808, 3210313671, 3336571891, 3584528711, 113926993, 338241895, 666307205, 773529912, 1294757372, 1396182291, 1695183700, 1986661051, 2177026350, 2456956037, 2730485921, 2820302411, 3259730800, 3345764771, 3516065817, 3600352804, 4094571909, 275423344, 430227734, 506948616, 659060556, 883997877, 958139571, 1322822218, 1537002063, 1747873779, 1955562222, 2024104815, 2227730452, 2361852424, 2428436474, 2756734187, 3204031479, 3329325298])[0],3609767458), new a(W[1],602891725), new a(W[2],3964484399), new a(W[3],2173295548), new a(W[4],4081628472), new a(W[5],3053834265), new a(W[6],2937671579), new a(W[7],3664609560), new a(W[8],2734883394), new a(W[9],1164996542), new a(W[10],1323610764), new a(W[11],3590304994), new a(W[12],4068182383), new a(W[13],991336113), new a(W[14],633803317), new a(W[15],3479774868), new a(W[16],2666613458), new a(W[17],944711139), new a(W[18],2341262773), new a(W[19],2007800933), new a(W[20],1495990901), new a(W[21],1856431235), new a(W[22],3175218132), new a(W[23],2198950837), new a(W[24],3999719339), new a(W[25],766784016), new a(W[26],2566594879), new a(W[27],3203337956), new a(W[28],1034457026), new a(W[29],2466948901), new a(W[30],3758326383), new a(W[31],168717936), new a(W[32],1188179964), new a(W[33],1546045734), new a(W[34],1522805485), new a(W[35],2643833823), new a(W[36],2343527390), new a(W[37],1014477480), new a(W[38],1206759142), new a(W[39],344077627), new a(W[40],1290863460), new a(W[41],3158454273), new a(W[42],3505952657), new a(W[43],106217008), new a(W[44],3606008344), new a(W[45],1432725776), new a(W[46],1467031594), new a(W[47],851169720), new a(W[48],3100823752), new a(W[49],1363258195), new a(W[50],3750685593), new a(W[51],3785050280), new a(W[52],3318307427), new a(W[53],3812723403), new a(W[54],2003034995), new a(W[55],3602036899), new a(W[56],1575990012), new a(W[57],1125592928), new a(W[58],2716904306), new a(W[59],442776044), new a(W[60],593698344), new a(W[61],3733110249), new a(W[62],2999351573), new a(W[63],3815920427), new a(3391569614,3928383900), new a(3515267271,566280711), new a(3940187606,3454069534), new a(4118630271,4000239992), new a(116418474,1914138554), new a(174292421,2731055270), new a(289380356,3203993006), new a(460393269,320620315), new a(685471733,587496836), new a(852142971,1086792851), new a(1017036298,365543100), new a(1126000580,2618297676), new a(1288033470,3409855158), new a(1501505948,4234509866), new a(1607167915,987167468), new a(1816402316,1246189591)],
  Q = [new a(0,1), new a(0,32898), new a(2147483648,32906), new a(2147483648,2147516416), new a(0,32907), new a(0,2147483649), new a(2147483648,2147516545), new a(2147483648,32777), new a(0,138), new a(0,136), new a(0,2147516425), new a(0,2147483658), new a(0,2147516555), new a(2147483648,139), new a(2147483648,32905), new a(2147483648,32771), new a(2147483648,32770), new a(2147483648,128), new a(0,32778), new a(2147483648,2147483658), new a(2147483648,2147516545), new a(2147483648,32896), new a(0,2147483649), new a(2147483648,2147516424)],
  K = [[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61], [28, 55, 25, 21, 56], [27, 20, 39, 8, 14]];

function get_signature(timestamp) {
    var r = new i("SHA-1", "TEXT");
      //, e = "password"
      //, s = "c3cef7c66a1843f8b3a9e6a1e3160e20";
    r.setHMACKey("d1b964811afb40118a12068ff74a12f4", "TEXT");
    r.update("password");
    r.update("c3cef7c66a1843f8b3a9e6a1e3160e20");
    r.update("com.zhihu.web");
    r.update(String(timestamp));
    return r.getHMAC("HEX")
}
var timestamp = Date.now();
console.log(get_signature(timestamp));