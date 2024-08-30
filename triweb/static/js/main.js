function any_to_date(date_str) {
    ts = Date.parse(date_str);
    if (!ts) {
        return null;
    }
    return new Date(ts);
}

function to_date_string(date) {
    if (! date) {
        return "";
    }
    let d = new Date(date);
    return d.toLocaleDateString("de", { year:"numeric", month:"short", day:"numeric"});
}

function to_datetime_string(date) {
    if (! date) {
        return "";
    }
    let d = new Date(date);
    return d.toLocaleTimeString("de", { year:"numeric", month:"short", day:"numeric"});
}


