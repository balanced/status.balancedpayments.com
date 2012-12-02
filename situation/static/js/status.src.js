var timer = null;
var intervalSeconds = 15;
var interval = 1000 * intervalSeconds;
var SERVICES = ['API', 'JS', 'DASH'];
var DISPLAYABLE_STATUSES = ['UP', 'DOWN', 'ISSUE'];
var ERROR_STATE = 'DOWN';

var loadData = function () {
    console.log('loading');
    loadUptime();
    loadMessages();
    loadCalendar();
};

var truncateDecimals = function(num, decimalPlaces) {
    if (!decimalPlaces) {
        decimalPlaces = 2;
    }
    var a = Math.pow(10, decimalPlaces);
    return Math.floor(num * a) / a;
};

var setServiceStatus = function (service, status) {
    $('.services.stc .' + service + ' .uptime-image')
        .removeClass('ISSUE')
        .removeClass('DOWN')
        .removeClass('UP')
        .addClass(status);
};

var loadUptime = function () {
    //  actual uptime of services
    $.get('/uptime', function (d) {
        console.log('uptime', d);
        for (var service in d.uptime) {
            var num = d.uptime[service].uptime;
            var status = d.uptime[service].status;
            if (num === 100) {
                num = num.toFixed(2);
            } else {
                num = truncateDecimals(num, 3).toFixed(3);
            }
            $('.' + service, '.uptime').find('h1').html(
                num + '<span>%</span>'
            );
            setServiceStatus(service, status);
        }
        setUpdated();
    });
};

var loadMessages = function (offset) {
    //  latest tweets
    $.get('/twitter/messages/latest', { offset: offset }, function (d) {
        for (var service in d.messages) {
            var msg = d.messages[service];
            var message;
            if (msg) {
                message = renderMessage(msg);
            } else {
                message = '<em>None</em>';
            }
            $('.' + service, '.recent-updates').html(message);
        }
        setUpdated();
    });
};

var loadCalendar = function (offset) {
    //  load the dates + messages
    $.get('/twitter/messages', { offset: offset }, function (d) {
        var min = new Date(d.messages.min * 1000),
            max = new Date(d.messages.max * 1000);

        delete d.messages.max;
        delete d.messages.min;

        console.log('tweets', d, min, max);

        var $root = $('.messages.stc ul');
        var $items = $root.find('li');
        var keys = [];
        var date;
        for (var dt = max; dt >= min; dt.setDate(dt.getDate() - 1)) {
            keys.push(new Date(dt).strftime('%Y-%m-%d'));
        }

        keys.sort();
        keys.reverse();

        for (var i in keys) {
            date = keys[i];
            var messages = d.messages;
            renderForDate($root, $items, date, messages, i);
        }
        evenColumnHeights();
        setUpdated();
    });
};

function renderForDate($root, $items, date, messages, index) {

    //  first entry or last entry
    var replaceable = $root.find('#date-' + date),
        elementIndex = $items.index($('#date-' + date));
    var dateFormat = elementIndex === 0 || (index == 0 && elementIndex === -1) ? '%b %d' : '%d';
    var dateParts = date.split('-');
    // is last day of month (month constructor is 0 indexed, day = 0 == previous day back)
    if (date == new Date(dateParts[0], dateParts[1], 0).strftime('%Y-%m-%d')) {
        dateFormat = '%b %d';
    }

    var dateEl = $('<div class="date"></div>').text(
        new Date(dateParts[0], dateParts[1] - 1, dateParts[2]).strftime(dateFormat)
    );
    var liEl = $('<li id="date-' + date + '"></li>');

    var hasMessages = false, hasErrors = false;
    dateEl.appendTo(liEl);

    // for each service check for messages and append as required. set some
    // global variables so we can alter the layout
    for (var service in SERVICES) {
        var _service = SERVICES[service];
        var serviceMessages = messages[_service];
        var messagesForDate = [];
        for (var i = 0; i < serviceMessages.length; i++) {
            var m = serviceMessages[i];
            if (new Date(m.created_at).strftime('%Y-%m-%d') === date) {
                messagesForDate.push(m);
            }
        }
        var result = renderServiceMessages(messagesForDate, _service);
        result.element.appendTo(liEl);
        if (result.hasMessages) {
            hasMessages = true;
        }
        if (result.hasErrors) {
            hasErrors = true;
        }
    }
    if (hasMessages) {
        liEl.addClass('messages').addClass('issues');
    }
    if (!replaceable.length) {
        var insertIndex = calculateIndex(date, $items);
        if (insertIndex === $items.length) {
            liEl.appendTo($root);
        } else {
            $root.find('> li').eq(insertIndex).before(liEl);
        }
    } else {
        replaceable.replaceWith(liEl);
    }
}

function calculateIndex(date, $items) {
    var dates = [];
    var dateAsDate = new Date(date);
    $items.each(function (i ,e) {
        var dateString = $(e).attr('id').replace('date-', '');
        dates.push(dateString);
    });
    //  sort as strings, javascript likes to sort date objects by Fri, Mon, Sat, Sun etc
    dates.sort();
    for (var i = 0 ; i < dates.length; i++) {
        var dt = new Date(dates[i]);
        if (dt < dateAsDate) {
            return i;
        }
    }
    return $items.length;
}

function renderServiceMessages(serviceMessages, srv) {
    var messageContainer = $('<div>&nbsp;</div>');
    var serviceHasError = false;
    var serviceHasMessage = false;
    var hasMessages = false, hasErrors = false;
    for (var i in serviceMessages) {
        var sm = serviceMessages[i];
        if (DISPLAYABLE_STATUSES.indexOf(sm.status) > -1) {
            $(renderMessage(sm)).appendTo(messageContainer);
            serviceHasMessage = true;
            if (sm.status === ERROR_STATE) {
                hasErrors = true;
                serviceHasError = true;
            }
        }
    }
    var pooel = $('<div class="' + srv + '"></div>');
    if (serviceHasMessage) {
        pooel.addClass('issues');
        if (serviceHasError) {
            pooel.addClass('errors');
        }
        hasMessages = true;
    }
    messageContainer.appendTo(pooel);
    return {
        'element':pooel,
        'hasErrors':hasErrors,
        'hasMessages':hasMessages
    };
}

function renderMessage(message) {
    var created_at = new Date(message.created_at);
    var formattedTime = created_at.strftime('%b %d @ %I:%M') + created_at.strftime('%p').toLowerCase();
    return '<div class="issue" data-state="' + message.status + '">' +
        '<p>' + linkify(message.message) + '</p>' +
        '<time datetime="' + created_at + '">' + formattedTime + '</time>' +
        '<a href="https://twitter.com/balancedstatus/status/' + message.tweet_id + '" class="tweet" target="_blank">@balancedstatus</a>' +
        '</div>';
}

function setUpdated() {
    var $tel = $('.stc.summary h2 time');
    var now = new Date();

    $tel.attr('datetime', now).text(
        now.strftime('%b %d, %Y @ %I:%M') + ' ' +
            now.strftime('%p').toLowerCase() + ' ' +
            now.strftime('%Z')
    );
}

function linkify(toLinkify) {
    var urlRegex = /\b(http|https)+(:\/\/)+(\S*)/ig;
    var matches = toLinkify.match(urlRegex);
    if (!matches) {
        return toLinkify;
    }
    for (var i = 0 ; i < matches.length ; i++) {
        var match = matches[i];
        toLinkify = toLinkify.replace(match,
            '<a href="' + match + '" target="_blank">' + match + '</a>');
    }
    return toLinkify;
}

function evenColumnHeights () {
    $('.messages.stc li.messages').each(function (i, $e) {
        var height = 0;
        $($e).find('.issues').each(function (_, li) {
            var h = $(li).height();
            if (h > height) {
                height = h;
            }
        });
        $($e).find('.issues > div').each(function (_, li) {
            var $li = $(li);
            var sib = $li.parent().children().length;
            $li.height(height / sib);
        });
    });
}

var Balanced = {
    init:function (params) {
        Status.init(params);
    }
};

var Status = {
    init:function (params) {
        loadData();
        timer = setInterval(loadData, interval);
        $('.load button').click(function (e) {
            loadCalendar($('.messages ul li').length);
        });
    }
};

Balanced.Status = Status;
