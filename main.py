import subprocess,shutil,os.path,argparse,signal,pygame,matter,sys,numpy as np,threading,queue

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
if args.node_path is None:
    # TODO: notify user that app depends on node
    raise NotImplementedError()
with subprocess.Popen([args.node_path, os.path.join( os.path.dirname(__file__), 'main.js', ) ]) as websocket_server, subprocess.Popen([ sys.executable, '-m', 'http.server', str(8080), '--directory', 'www', ]) as http_server:
    data=queue.Queue()
    stop=threading.Event()
    def websocket_connect_as_client():
        from websockets.sync.client import connect
        from json import dumps
        # from time import time as current_time
        with connect(f'ws://localhost:{8032}') as websocket_client:
            while not stop.wait(timeout=1.):
                try:
                    while True:
                        websocket_client.send(dumps(data.get_nowait()))
                except queue.Empty:
                    pass
                # and then we wait another second
            # if the above works normally there should be no leftover data
            # send leftover data
            # try:
            #     # this is inefficient and blocks
            #     while True:
            #         websocket_client.send(dumps(data.get_nowait()))
            # except queue.Empty:
            #     pass
        print('streaming thread exited')
    streaming_thread=threading.Thread(target=websocket_connect_as_client)
    streaming_thread.start()

    new_velocity=queue.Queue()
    def ui_communication_agent():
        from websockets.sync.client import connect
        from json import loads
        with connect(f'ws://localhost:{8032}') as websocket_client:
            while not stop.is_set():
                try:
                    data=loads(websocket_client.recv(timeout=0))
                    if data['type']=='push':
                        new_velocity.put_nowait(data['value'])
                except TimeoutError:
                    pass
        print('ui thread exited')
    ui_thread=threading.Thread(target=ui_communication_agent)
    ui_thread.start()


    # import webbrowser
    # webbrowser.open(f'localhost:{8080}')

    WIDTH,HEIGHT=1280,720 # will be used for links acting as walls later on
    PARTICLE_VELOCITY=1.

    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True
    dt = 0
    time = 0

    point=matter.Node(10,np.array([0.,100.]),np.array([PARTICLE_VELOCITY,0.]))
    scene=matter.System()
    scene.add(point)

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        data.put_nowait({
            'type': 'data',
            'pos': point.pos[0],
            'time': time,
            'accel': 0,
            'vel': (point.pos-point.ppos)[0],
        })
        try:
            point.ppos = point.pos - np.array([new_velocity.get_nowait(),0.])
        except queue.Empty:
            pass

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("black")

        for node in scene.nodes:
            pygame.draw.circle(screen,'white',node.pos,node.rad)
        scene.update(dt)

        # flip() the display to put your work on screen
        pygame.display.flip()

        # limits FPS to 60
        # dt is delta time in seconds since last frame, used for framerate-
        # independent physics.
        dt = clock.tick(60) / 1000
        time += dt

    pygame.quit()
    # send SIGINT when pygame event loop exits
    stop.set()
    streaming_thread.join()
    ui_thread.join()
    websocket_server.send_signal(signal.SIGINT)
    http_server.send_signal(signal.SIGINT)
