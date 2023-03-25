import sys
from Cocoa import NSObject, NSApplication, NSApp, NSWindow, NSBackingStoreBuffered, NSMakeRect

class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        # Create a window
        window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(0, 0, 400, 200),
            15,
            NSBackingStoreBuffered,
            False,
        )
        window.center()
        window.setTitle_("My Python Mac App")
        window.makeKeyAndOrderFront_(None)

if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    app.run()