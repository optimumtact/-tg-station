#define PATH_FIND_START 1
#define PATH_FIND_END 2

/datum/path_debug
	var/client/holder
	var/datum/callback/li_cb
	var/list/preview

	// SECTION UI
	var/list/buttons

	var/turf/start
	var/turf/end

	//client specific images
	var/image/startimage
	var/image/endimage

/datum/path_debug/New(client/c)
	holder = c
	buttons = list()
	li_cb = CALLBACK(src, .proc/post_login)
	holder.player_details.post_login_callbacks += li_cb
	holder.show_popup_menus = FALSE
	create_buttons()
	holder.screen += buttons
	holder.click_intercept = src


/datum/path_debug/proc/quit()
	qdel(src)

/datum/path_debug/Destroy()
	holder.screen -= buttons
	holder.click_intercept = null
	holder.show_popup_menus = TRUE
	holder.player_details.post_login_callbacks -= li_cb
	holder.images -= startimage
	holder.images -= endimage
	holder = null
	startimage = null
	endimage= null
	QDEL_LIST(buttons)
	return ..()

/datum/path_debug/proc/post_login()
	// since these will get wiped upon login
	holder.screen += buttons

/datum/path_debug/proc/create_buttons()
	buttons += new /obj/screen/path_debug/mode(src)
	buttons += new /obj/screen/path_debug/help(src)
	buttons += new /obj/screen/path_debug/find(src)

/datum/path_debug/proc/select_tile(turf/T, type_to_select)
	var/overlaystate
	switch(type_to_select)
		if(PATH_FIND_START)
			if(startimage)
				holder.images -= startimage
			overlaystate = "greenOverlay"
			startimage = image('icons/turf/overlays.dmi', T, overlaystate)
			startimage.plane = ABOVE_LIGHTING_PLANE
			holder.images += startimage
			return T
		if(PATH_FIND_END)
			if(endimage)
				holder.images -= endimage
			overlaystate = "blueOverlay"
			endimage = image('icons/turf/overlays.dmi', T, overlaystate)
			endimage.plane = ABOVE_LIGHTING_PLANE
			holder.images += endimage
			return T

	return T

/datum/path_debug/proc/show_help()
	to_chat(holder, "Left click to set the start node, right click to set the end node")

/datum/path_debug/proc/toggle_pathfinder()
	to_chat(holder, "Toggling pathfinder type")

/datum/path_debug/proc/start_pathfind()
	to_chat(holder, "Starting pathfinder")


/datum/path_debug/proc/InterceptClickOn(mob/user, params, atom/object)
	var/list/pa = params2list(params)
	var/left_click = pa.Find("left")
	var/right_click = pa.Find("right")
	if(left_click)
		start = select_tile(get_turf(object), PATH_FIND_START)
		return TRUE
	if(right_click)
		end = select_tile(get_turf(object), PATH_FIND_END)
		return TRUE
	return TRUE // no doing underlying actions

/proc/togglepathmode(mob/M as mob in GLOB.player_list)
	if(M.client)
		if(istype(M.client.click_intercept,/datum/path_debug))
			var/datum/path_debug/p = M.client.click_intercept
			p.quit()
			log_admin("[key_name(usr)] has left pathfinder debug mode.")
		else
			new /datum/path_debug(M.client)
			message_admins("[key_name_admin(usr)] has entered pathfinder debug mode.")
			log_admin("[key_name(usr)] has entered pathfinder debug mode.")

#undef PATH_FIND_START
#undef PATH_FIND_END
