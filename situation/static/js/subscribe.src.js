function isEmpty(element) {
    if($(element).val() === "") {
        $(element).closest(".control-group").addClass("error");
        return true;
    }

    $(element).closest(".control-group").removeClass("error");
    return false;
}

function getCheckedValues(check_elements) {
    var checked = "";

    $(check_elements).each(function() {
        if($(this).is(":checked")) {
            checked += $(this).val() + ",";
        }
    });

    return checked;
}

function hasChecked(check_elements) {
    if(getCheckedValues(check_elements).length === 0) {
        $(check_elements).closest(".control-group").addClass("error");
        return false;
    }

    $(check_elements).closest(".control-group").removeClass("error");
    return true;
}

function disableFields(section) {
    $(section).find("input, button").prop("disabled", true);
}

function enableFields(section) {
    $(section).find("input, button").prop("disabled", false);
}

function sanitizePhone(phone) {
    return phone.replace(/ /g, "").replace(/-/g, "").replace(/\(/g, "").replace(/\)/g, "");
}

$(document).ready(function() {
    $("#subscribe .base").click(function() {
        if($("#subscribe .content").is(":visible")) {
            $("#subscribe .base .copy").html("Subscribe to notifications").removeClass("close-content");
        } else {
            $("#subscribe .base .copy").html("Close").addClass("close-content");
        }

        $("#subscribe .content").slideToggle("fast");
    });

    $("#subscribe .section-toggle").click(function() {
        if($(this).closest("section").hasClass("open")) {
            return;
        }

        $("#subscribe section.open").removeClass("open");

        if($("#subscribe .section-content:visible").length === 0) {
            $(this).closest("section").addClass("open");
            $(this).next(".section-content").slideDown("fast");
        } else {
            $("#subscribe .section-content:visible").slideUp("fast");
            $(this).closest("section").addClass("open");
            $(this).next(".section-content").slideDown("fast");
        }
    });

    $("#sms-submit").click(function() {
        if($(this).prop("disabled")) {
            return;
        }

        var p = $("#sms-phone");
        var services = $("#subscribe input[name='sms-subscribe[]']");

        if(!isEmpty(p) && hasChecked(services)) {
            disableFields($("#sms"));

            $.ajax("/subscriptions/sms", {
                type: 'POST',
                dataType: 'json',
                data: {
                    phone: sanitizePhone($(p).val()),
                    services: getCheckedValues(services)
                },
                success: function(result) {
                    $("#sms .section-content .result.subscribed").show();
                },
                complete: function(result) {
                    if(result.status !== 200) {
                        var responseObject = JSON.parse(result.responseText);

                        enableFields($("#sms"));
                        $("#sms .section-content .result.error span").html(responseObject.error);
                        $("#sms .section-content .result.error").show();
                    }
                }
            });
        }
    });

    $("#e-submit").click(function() {
        if($(this).prop("disabled")) {
            return;
        }

        var e = $("#e-email");
        var services = $("#subscribe input[name='e-subscribe[]']");

        if(!isEmpty(e) && hasChecked(services)) {
            disableFields($("#email"));

            $.ajax("/subscriptions/email", {
                type: 'POST',
                dataType: 'json',
                data: {
                    email: $(e).val(),
                    services: getCheckedValues(services)
                },
                success: function(result) {
                    $("#email .section-content .result.subscribed").show();
                },
                complete: function(result) {
                    if(result.status !== 200) {
                        var responseObject = JSON.parse(result.responseText);

                        enableFields($("#email"));
                        $("#email .section-content .result.error span").html(responseObject.error);
                        $("#email .section-content .result.error").show();
                    }
                }
            });
        }
    });
});