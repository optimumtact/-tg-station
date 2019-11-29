/obj/screen/path_debug
	icon = 'icons/misc/buildmode.dmi'
	var/datum/path_debug/pd
	// If we don't do this, we get occluded by item action buttons
	layer = ABOVE_HUD_LAYER

/obj/screen/path_debug/New(datum/path_debug/ppd)
	pd = ppd
	return ..()

/obj/screen/path_debug/Destroy()
	pd = null
	return ..()

/obj/screen/path_debug/mode
	name = "Toggle Pathfinding Mode"
	icon_state = "buildmode_basic"
	screen_loc = "NORTH,WEST"

/obj/screen/path_debug/mode/Click(location, control, params)
	pd.toggle_pathfinder()
	return 1

/obj/screen/path_debug/help
	icon_state = "buildhelp"
	screen_loc = "NORTH,WEST+1"
	name = "Pathfinder Help"

/obj/screen/path_debug/help/Click(location, control, params)
	pd.show_help()
	return 1

/obj/screen/path_debug/find
	icon_state = "build"
	screen_loc = "NORTH,WEST+2"
	name = "Start pathfinder"

/obj/screen/path_debug/find/Click()
	pd.start_pathfind()
	return 1
