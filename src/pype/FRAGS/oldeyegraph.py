
class old_EyeGraph(DockWindow):
	def __init__(self, **options):
		options['title'] = 'eyegraph'
		options['iconname'] = 'eyegraph'
		apply(DockWindow.__init__, (self,), options)

		self.xt = Graph(self, title='', plotbackground='gray50',
					   height=200, width=700)
		self.xt.pack(expand=1, fill=BOTH)
		self.xt.axis_configure(XAXIS, hide=0)
		self.xt.axis_configure(YAXIS, hide=0)
		self.xt.legend_configure(hide=1)
		self.xt.element_create('horiz',symbol='', color='red')
		self.xt.element_create('vert', symbol='', color='green')
		self.xt.element_create('raster', symbol='square', color='white',
							   pixels=1, linewidth=0)
		self.xt.element_create('v1', color='white', fill='green',
							   linewidth=0, symbol='circle', pixels=5)
		self.xt.element_create('v2', color='white', fill='red',
							   linewidth=0, symbol='circle', pixels=5)
		self.start = None
		self.stop = None

	def show(self, start=None, stop=None):
		self.start = start
		self.stop = stop

	def update(self, t=None, x=None, y=None, raster=None):
		if len(t) > 0 and self._visible:
			t0 = t[0]
			t = (t - t[0]) / 1000.0
			
			if x and y:
				z1 = max([max(x),max(y)])
				z2 = min([min(x),min(y)])
			else:
				z1 = 0
				z2 = 0

			#self.xt.axis_configure(YAXIS, max=z1, min=z2)

			if self.start and self.stop and (self.start < self.stop):
				self.xt.axis_configure(XAXIS,
									   min=(self.start-t0)/1000.0,
									   max=(self.stop-t0)/1000.0)
			else:
				self.xt.axis_configure(XAXIS, min=t[0], max=t[-1])

			if self.start:
				self.xt.element_configure('v1',
										 xdata=((self.start-t0)/1000.0,),
										 ydata=((z1+z2)/2,), hide=0)
			else:
				self.xt.element_configure('v1', hide=1)
				

			if self.stop:
				self.xt.element_configure('v2',
										 xdata=((self.stop-t0)/1000.0,),
										 ydata=((z1+z2)/2,), hide=0)
			else:
				self.xt.element_configure('v2', hide=1)

			if x and t:
				self.xt.element_configure('horiz', 
										  xdata=tuple(t), ydata=tuple(x))
			if y and t:
				self.xt.element_configure('vert',
										 xdata=tuple(t), ydata=tuple(y))
			if None and raster and t and x and y:
				z = [round(z1 - 0.25 * (z1 - z2))] * len(raster)
				self.xt.element_configure('raster',
						  ydata=tuple(z),
						  xdata=tuple((array(raster)-t0)/1000.0))
