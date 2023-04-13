/proc/main()
	world.log << "Main proc!!"

/world/New()
	world.log << "--------------------"
	main()
	world.log << "--------------------"
	shutdown()
