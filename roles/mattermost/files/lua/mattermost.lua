local json = require "json"
local http = require "resty.http"

local function ret_error(id, message, status)
    ngx.status = status
    ngx.header.content_type = 'application/json'
    ngx.header["X-Request-Id"] = ngx.var.request_id
    ngx.say(json.encode({
        id=id,
        message=message,
        request_id=ngx.var.request_id,
        detailed_error="",
        status_code=status,
    }))
    ngx.exit(status)
end

local function get_body()
    ngx.req.read_body()
    return json.decode(ngx.req.get_body_data() or "{}")
end

local function get_mm(endpoint)
    local httpc = http.new()
    local uri = "http://127.0.0.1:8065/api/v4" .. endpoint

    local req_headers = ngx.req.get_headers()
    local res, err = httpc:request_uri(uri, { headers = {
	["Cookie"] = req_headers["Cookie"],
	["Authorization"] = req_headers["Authorization"],
    }})
    if not res then
        ret_error("api.internal_error",
                  "Internal error when verifying permissions. Please contact administrators. " .. err,
                  500)
    end

    if res.status == 403 then
        ret_error("api.context.permission.app_error",
                  "Only team administrators can modify channel properties",
                  403)
    end

    if res.status ~= 200 then
        ret_error("api.internal_error",
                  "Internal error when verifying permissions. Please contact administrators. " .. res.body,
                  500)
    end
    return json.decode(res.body)
end

local function endswith(s, x)
    return x == "" or string.sub(s, -#x) == x
end

local function valid_email(email)
    return endswith(email, "@srcf.net") or endswith(email, "@cam.ac.uk") or endswith(email, ".cam.ac.uk")
end

local function match(pattern, method)
    if ngx.var.request_method ~= method then
        return false
    end
    ngx.ctx.capture = string.match(ngx.var.uri, "^/api/v4" .. pattern .. "$")
    return ngx.ctx.capture ~= nil
end

-- Only allow @srcf or @cam email addresses, unless invited.
if match("/users", "POST") then
    local args = ngx.req.get_uri_args()
    -- Allow invited people. Mattermost will check if this is a valid
    -- invitation.
    if args["iid"] ~= nil or args["t"] ~= nil then
        return
    end
    local obj = get_body()
    local email = obj["email"] or ""
    if not valid_email(email) then
        ret_error("api.user.create_user.accepted_domain.app_error",
                  "You must use an @srcf.net or @cam.ac.uk email unless you have an invitation.",
                  400)
    end
    -- Forbid open team
elseif match("/teams/[a-z0-9]*/privacy", "PUT") then
    local obj = get_body()
    if obj["privacy"] == "O" then
        ret_error("api.context.permission.app_error",
                  "Open teams are not allowed on this server",
                  403)
    end
    -- Forbid open team
elseif match("/teams/[a-z0-9]*/patch", "PUT") or
    match("/teams/[a-z0-9]*", "PUT") then
    local obj = get_body()
    if obj["allow_open_invite"] then
        ret_error("api.context.permission.app_error",
                  "Open teams are not allowed on this server",
                  403)
    end
    -- Only allow team admins to manage channels
elseif match("/channels", "POST") then
    local obj = get_body()

    local perms = get_mm("/teams/" .. obj["team_id"] .. "/members/" ..  ngx.var.cookie_MMUSERID)
    if not perms["scheme_admin"] then
        ret_error("api.context.permission.app_error",
                  "Only team administrators can create channels",
                  403)
    end
elseif match("/channels/([a-z0-9]*)", "DELETE") or
    match("/channels/([a-z0-9]*)", "PUT") or
    match("/channels/([a-z0-9]*)/patch", "PUT") then
    local team_id = get_mm("/channels/" .. ngx.ctx.capture)["team_id"]
    local perms = get_mm("/teams/" .. team_id .. "/members/" ..  ngx.var.cookie_MMUSERID)
    if not perms["scheme_admin"] then
        ret_error("api.context.permission.app_error",
                  "Only team administrators can modify channels properties",
                  403)
    end
end
