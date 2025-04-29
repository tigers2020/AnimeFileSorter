#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AnimeFileSorter 애플리케이션 진입점
"""

import asyncio
from src.app import main

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 