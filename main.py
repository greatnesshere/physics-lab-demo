import subprocess,shutil,os.path,argparse,signal,pygame,matter,sys,numpy as np,json,threading,queue,time

parser=argparse.ArgumentParser(
    prog='PhysioLab',
    description='PhysioLab',
    epilog='@greatnesshere',
)
parser.add_argument(
    '--node-path',
    action='store',
    help='specify a path to a NodeJS executable '
         '(defaults to shell PATH node)',
    default=shutil.which('node'),
)
args=parser.parse_args()
if args.node_path is not None:
    with subprocess.Popen([
        args.node_path,
        os.path.join(
            os.path.dirname(__file__),
            'main.js',
        )
    ]) as websocket_server, subprocess.Popen([
        sys.executable,
        '-m',
        'http.server',
        str(8080),
        '--directory',
        'www',
    ]) as http_server:
        # import webbrowser
        # webbrowser.open(f'localhost:{8080}')
        WIDTH,HEIGHT=1280,720 # will be used for links acting as walls later on
        PARTICLE_VELOCITY=1.
        # pygame setup
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        clock = pygame.time.Clock()
        RUNNING = True
        DT = 0
        TIME = 0

        point=matter.Node(10,np.array([0.,100.]),np.array([PARTICLE_VELOCITY,0.]))
        scene=matter.System()
        scene.add(point)

        data=queue.Queue()
        stop=threading.Event()

        def stream():
            while True:
                time.sleep(1.)
                if websocket_server.stdin is not None:
                    json.dump(
                        data.get(),
                        websocket_server.stdin
                    )
                if stop.is_set():
                    break
        streaming_thread=threading.Thread(target=stream)
        streaming_thread.start()

        while RUNNING:
            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    RUNNING = False

            data.put_nowait(
                {
                    'pos': point.pos[0],
                    'time': TIME,
                    'accel': 0,
                    'vel': (point.pos-point.ppos)[0],
                },
            )

            # fill the screen with a color to wipe away anything from last frame
            screen.fill("black")

            for node in scene.nodes:
                pygame.draw.circle(screen,'white',node.pos,node.rad)
            scene.update(DT)

            # flip() the display to put your work on screen
            pygame.display.flip()

            # limits FPS to 60
            # dt is delta time in seconds since last frame, used for framerate-
            # independent physics.
            DT = clock.tick(60) / 1000
            TIME += DT

        pygame.quit()
        # send SIGINT when pygame event loop exits
        stop.set()
        websocket_server.send_signal(signal.SIGINT)
        http_server.send_signal(signal.SIGINT)
        streaming_thread.join()
else:
    # TODO: notify user that app depends on node
    raise NotImplementedError()
