#!/usr/bin/python

import controller


def main ():
    cr = controller.Controller.get_instance()
    cr.start()

if __name__ == "__main__":
    main()


