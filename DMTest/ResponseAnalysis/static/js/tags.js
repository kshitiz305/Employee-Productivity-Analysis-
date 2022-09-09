(function (c) {
	var d = {
            prefilled: ['gaa','ort','fpx','lpx','prd','"PRD-PX"'], 
            CapitalizeFirstLetter: false,
			preventSubmitOnEnter: true,
			isClearInputOnEsc: true,
			externalTagId: false,
			prefillIdFieldName: "Id",
			prefillValueFieldName: "Value",
			AjaxPush: null,
			AjaxPushAllTags: null,
			AjaxPushParameters: null,
			delimiters: [9, 13, 44],
			backspace: [8],
			maxTags: 0,
			hiddenTagListName: null,
			hiddenTagListId: null,
			replace: true,
			output: null,
			deleteTagsOnBackspace: true,
			tagsContainer: null,
			tagCloseIcon: "x",
			tagClass: "",
			validator: null,
			onlyTagList: false,
			tagList: null,
			fillInputOnTagRemove: false
		},
		a = {
			pushTag: function (z, g, h) {
				var y = c(this),
					r = y.data("opts"),
					l, e, x, v, j = y.data("tlis"),
					t = y.data("tlid"),
					s, p, q, k, n, A, f, o;
				z = b.trimTag(z, r.delimiterChars);
				if (!z || z.length <= 0) {
					return
				}
				if (r.onlyTagList && undefined !== r.tagList) {
					if (r.tagList) {
						var m = r.tagList;
						c.each(m, function (i, B) {
							m[i] = B.toLowerCase()
						});
						var u = c.inArray(z.toLowerCase(), m);
						if (-1 === u) {
							return
						}
					}
				}
				if (r.CapitalizeFirstLetter && z.length > 1) {
					z = z.charAt(0).toUpperCase() + z.slice(1).toLowerCase()
				}
				if (r.validator && !r.validator(z)) {
					y.trigger("tm:invalid", z);
					return
				}
				if (r.maxTags > 0 && j.length >= r.maxTags) {
					return
				}
				l = false;
				e = jQuery.map(j, function (i) {
					return i.toLowerCase()
				});
				s = c.inArray(z.toLowerCase(), e);
				if (-1 !== s) {
					l = true
				}
				if (l) {
					y.trigger("tm:duplicated", z);
					if (r.blinkClass) {
						for (var w = 0; w < 6; ++w) {
							c("#" + y.data("tm_rndid") + "_" + t[s]).queue(function (i) {
								c(this).toggleClass(r.blinkClass);
								i()
							}).delay(100)
						}
					} else {
						c("#" + y.data("tm_rndid") + "_" + t[s]).stop().animate({
							backgroundColor: r.blinkBGColor_1
						}, 100).animate({
							backgroundColor: r.blinkBGColor_2
						}, 100).animate({
							backgroundColor: r.blinkBGColor_1
						}, 100).animate({
							backgroundColor: r.blinkBGColor_2
						}, 100).animate({
							backgroundColor: r.blinkBGColor_1
						}, 100).animate({
							backgroundColor: r.blinkBGColor_2
						}, 100)
					}
				} else {
					if (r.externalTagId === true) {
						if (h === undefined) {
							c.error("externalTagId is not passed for tag -" + z)
						}
						v = h
					} else {
						x = Math.max.apply(null, t);
						x = x === -Infinity ? 0 : x;
						v = ++x
					}
					if (!g) {
						y.trigger("tm:pushing", [z, v])
					}
					j.push(z);
					t.push(v);
					if (!g) {
						if (r.AjaxPush !== null && r.AjaxPushAllTags == null) {
							if (c.inArray(z, r.prefilled) === -1) {
								c.post(r.AjaxPush, c.extend({
									tag: z
								}, r.AjaxPushParameters))
							}
						}
					}
					p = y.data("tm_rndid") + "_" + v;
					q = y.data("tm_rndid") + "_Remover_" + v;
					k = c("<span/>").text(z).html();
					n = '<span class="' + b.tagClasses.call(y) + '" id="' + p + '">';
					n += "<span>" + k + "</span>";
					n += '<a href="#" class="tm-tag-remove" id="' + q + '" TagIdToRemove="' + v + '">';
					n += r.tagCloseIcon + "</a></span> ";
					A = c(n);
					if (r.tagsContainer !== null) {
						c(r.tagsContainer).append(A)
					} else {
						if (t.length > 1) {
							o = y.siblings("#" + y.data("tm_rndid") + "_" + t[t.length - 2]);
							o.after(A)
						} else {
							y.before(A)
						}
					}
					A.find("#" + q).on("click", y, function (B) {
						B.preventDefault();
						var i = parseInt(c(this).attr("TagIdToRemove"));
						b.spliceTag.call(y, i, B.data)
					});
					b.refreshHiddenTagList.call(y);
					if (!g) {
						y.trigger("tm:pushed", [z, v])
					}
					b.showOrHide.call(y)
				}
				y.val("")
			},
			popTag: function () {
				var i = c(this),
					g, f, h = i.data("tlis"),
					e = i.data("tlid");
				if (e.length > 0) {
					g = e.pop();
					f = h[h.length - 1];
					i.trigger("tm:popping", [f, g]);
					h.pop();
					c("#" + i.data("tm_rndid") + "_" + g).remove();
					b.refreshHiddenTagList.call(i);
					i.trigger("tm:popped", [f, g])
				}
			},
			empty: function () {
				var h = c(this),
					g = h.data("tlis"),
					e = h.data("tlid"),
					f;
				while (e.length > 0) {
					f = e.pop();
					g.pop();
					c("#" + h.data("tm_rndid") + "_" + f).remove();
					b.refreshHiddenTagList.call(h)
				}
				h.trigger("tm:emptied", null);
				b.showOrHide.call(h)
			},
			tags: function () {
				var f = this,
					e = f.data("tlis");
				return e
			}
		},
		b = {
			showOrHide: function () {
				var g = this,
					e = g.data("opts"),
					f = g.data("tlis");
				if (e.maxTags > 0 && f.length < e.maxTags) {
					g.show();
					g.trigger("tm:show")
				}
				if (e.maxTags > 0 && f.length >= e.maxTags) {
					g.hide();
					g.trigger("tm:hide")
				}
			},
			tagClasses: function () {
				var i = c(this),
					g = i.data("opts"),
					h = g.tagBaseClass,
					e = g.inputBaseClass,
					f;
				f = h;
				if (i.attr("class")) {
					c.each(i.attr("class").split(" "), function (j, k) {
						if (k.indexOf(e + "-") !== -1) {
							f += " " + h + k.substring(e.length)
						}
					})
				}
				f += (g.tagClass ? " " + g.tagClass : "");
				return f
			},
			trimTag: function (e, f) {
				var g;
				e = c.trim(e);
				g = 0;
				for (g; g < e.length; g++) {
					if (c.inArray(e.charCodeAt(g), f) !== -1) {
						break
					}
				}
				return e.substring(0, g)
			},
			refreshHiddenTagList: function () {
				var g = c(this),
					f = g.data("tlis"),
					e = g.data("lhiddenTagList");
				if (e) {
					c(e).val(f.join(g.data("opts").baseDelimiter)).change()
				}
				g.trigger("tm:refresh", f.join(g.data("opts").baseDelimiter))
			},
			killEvent: function (f) {
				f.cancelBubble = true;
				f.returnValue = false;
				f.stopPropagation();
				f.preventDefault()
			},
			keyInArray: function (g, f) {
				return c.inArray(g.which, f) !== -1
			},
			applyDelimiter: function (f) {
				var g = c(this);
				a.pushTag.call(g, c(this).val());
				f.preventDefault()
			},
			prefill: function (e) {
				var g = c(this);
				var f = g.data("opts");
				c.each(e, function (h, i) {
					if (f.externalTagId === true) {
						a.pushTag.call(g, i[f.prefillValueFieldName], true, i[f.prefillIdFieldName])
					} else {
						a.pushTag.call(g, i, true)
					}
				})
			},
			pushAllTags: function (i, f) {
				var j = c(this),
					g = j.data("opts"),
					h = j.data("tlis");
				if (g.AjaxPushAllTags) {
					if (i.type !== "tm:pushed" || c.inArray(f, g.prefilled) === -1) {
						c.post(g.AjaxPush, c.extend({
							tags: h.join(g.baseDelimiter)
						}, g.AjaxPushParameters))
					}
				}
			},
			spliceTag: function (h) {
				var j = this,
					i = j.data("tlis"),
					f = j.data("tlid"),
					e = c.inArray(h, f),
					g;
				if (-1 !== e) {
					g = i[e];
					j.trigger("tm:splicing", [g, h]);
					c("#" + j.data("tm_rndid") + "_" + h).remove();
					i.splice(e, 1);
					f.splice(e, 1);
					b.refreshHiddenTagList.call(j);
					j.trigger("tm:spliced", [g, h])
				}
				b.showOrHide.call(j)
			},
			init: function (e) {
				var f = c.extend({}, d, e),
					g, h;
				f.hiddenTagListName = (f.hiddenTagListName === null) ? "hidden-" + this.attr("name") : f.hiddenTagListName;
				g = f.delimeters || f.delimiters;
				h = [9, 13, 17, 18, 19, 37, 38, 39, 40];
				f.delimiterChars = [];
				f.delimiterKeys = [];
				c.each(g, function (k, j) {
					if (c.inArray(j, h) !== -1) {
						f.delimiterKeys.push(j)
					} else {
						f.delimiterChars.push(j)
					}
				});
				f.baseDelimiter = String.fromCharCode(f.delimiterChars[0] || 44);
				f.tagBaseClass = "tm-tag";
				f.inputBaseClass = "tm-input";
				if (!c.isFunction(f.validator)) {
					f.validator = null
				}
				this.each(function () {
					var o = c(this),
						j = "",
						n = "",
						m = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
					if (o.data("tagManager")) {
						return false
					}
					o.data("tagManager", true);
					for (var l = 0; l < 5; l++) {
						n += m.charAt(Math.floor(Math.random() * m.length))
					}
					o.data("tm_rndid", n);
					o.data("opts", f).data("tlis", []).data("tlid", []);
					if (f.output === null) {
						j = c("<input/>", {
							type: "hidden",
							name: f.hiddenTagListName
						});
						o.after(j);
						o.data("lhiddenTagList", j)
					} else {
						o.data("lhiddenTagList", c(f.output))
					}
					if (f.AjaxPushAllTags) {
						o.on("tm:spliced", b.pushAllTags);
						o.on("tm:popped", b.pushAllTags);
						o.on("tm:pushed", b.pushAllTags)
					}
					o.on("focus keypress", function (i) {
						if (c(this).popover) {
							c(this).popover("hide")
						}
					});
					if (f.isClearInputOnEsc) {
						o.on("keyup", function (i) {
							if (i.which === 27) {
								c(this).val("");
								b.killEvent(i)
							}
						})
					}
					o.on("keypress", function (i) {
						if (b.keyInArray(i, f.delimiterChars)) {
							b.applyDelimiter.call(o, i)
						}
					});
					o.on("keydown", function (i) {
						if (i.which === 13) {
							if (f.preventSubmitOnEnter) {
								b.killEvent(i)
							}
						}
						if (b.keyInArray(i, f.delimiterKeys)) {
							b.applyDelimiter.call(o, i)
						}
					});
					if (f.deleteTagsOnBackspace) {
						o.on("keydown", function (i) {
							if (b.keyInArray(i, f.backspace)) {
								if (c(this).val().length <= 0) {
									a.popTag.call(o);
									b.killEvent(i)
								}
							}
						})
					}
					if (f.fillInputOnTagRemove) {
						o.on("tm:popped", function (p, i) {
							c(this).val(i)
						})
					}
					o.change(function (i) {
						if (!/webkit/.test(navigator.userAgent.toLowerCase())) {
							o.focus()
						}
						b.killEvent(i)
					});
					if (f.prefilled !== null) {
						if (typeof (f.prefilled) === "object") {
							b.prefill.call(o, f.prefilled)
						} else {
							if (typeof (f.prefilled) === "string") {
								b.prefill.call(o, f.prefilled.split(f.baseDelimiter))
							} else {
								if (typeof (f.prefilled) === "function") {
									b.prefill.call(o, f.prefilled())
								}
							}
						}
					} else {
						if (f.output !== null) {
							if (c(f.output) && c(f.output).val()) {
								var k = c(f.output)
							}
							b.prefill.call(o, c(f.output).val().split(f.baseDelimiter))
						}
					}
				});
				return this
			}
		};
	c.fn.tagsManager = function (f) {
		var e = c(this);
		if (!(0 in this)) {
			return this
		}
		if (a[f]) {
			return a[f].apply(e, Array.prototype.slice.call(arguments, 1))
		} else {
			if (typeof f === "object" || !f) {
				return b.init.apply(this, arguments)
			} else {
				c.error("Method " + f + " does not exist.");
				return false
			}
		}
	}
}(jQuery));