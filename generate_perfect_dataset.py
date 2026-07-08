import os
import csv
import re

# Directory creation
os.makedirs("e:\\DATASET\\dataset\\processed", exist_ok=True)

# Order of semesters for sorting and checking consecutiveness
semester_order = {
    "Winter 2021": 2021.5,
    "Summer 2022": 2022.0,
    "Winter 2022": 2022.5,
    "Summer 2023": 2023.0,
    "Winter 2023": 2023.5,
    "Summer 2024": 2024.0,
    "Winter 2024": 2024.5,
    "Summer 2025": 2025.0,
    "Winter 2025": 2025.5
}

def sort_semesters(sem_list):
    return sorted(sem_list, key=lambda s: semester_order.get(s, 9999.0))

def check_consecutive_semesters(sem_list):
    # Extracts year numbers and checks if there are consecutive years
    years = sorted(list(set([int(re.search(r'\d{4}', s).group()) for s in sem_list if re.search(r'\d{4}', s)])))
    for i in range(len(years) - 1):
        if years[i+1] - years[i] == 1:
            return True
    return False

# ==============================================================================
# EMBEDDED SYSTEMS DATA DEFINITIONS
# ==============================================================================

es_unique_questions = {
    "1.1": {
        "text": "Define and classify Embedded Systems, and list examples of such systems.",
        "chapter": "1. Introduction to Embedded Systems",
        "difficulty": "Easy",
        "raw_matches": [
            ("Summer 2022", 3, "Define and classify the embedded systems, give few examples of such systems."),
            ("Winter 2023", 3, "Define Embedded system. Describe its type with two example of each."),
            ("Winter 2024", 3, "Define Embedded Systems."),
            ("Summer 2025", 4, "What is and Embedded system? What are its characteristics?"),
            ("Summer 2024", 4, "What is mean by embedded systems? What are the components of it? Give examples of embedded system."),
            ("Winter 2022", 3, "Classify Embedded system and discuss the various components of embedded system design in brief.")
        ]
    },
    "1.2": {
        "text": "Describe the components of an Embedded System.",
        "chapter": "1. Introduction to Embedded Systems",
        "difficulty": "Easy",
        "raw_matches": [
            ("Winter 2024", 4, "Describe the components of an Embedded System.")
        ]
    },
    "1.3": {
        "text": "Describe the skills required for an embedded system designer.",
        "chapter": "1. Introduction to Embedded Systems",
        "difficulty": "Easy",
        "raw_matches": [
            ("Winter 2021", 7, "Describe the various skills required for an embedded system designer as per embedded system classification."),
            ("Summer 2022", 4, "Describe skills required for embedded design engineer."),
            ("Summer 2023", 3, "Write down the skills required for an Embedded System Designer."),
            ("Summer 2025", 3, "Write down skills Required for an Embedded System Designer.")
        ]
    },
    "1.4": {
        "text": "Describe an embedded processor as GPP, ASIP and Single purpose processor.",
        "chapter": "1. Introduction to Embedded Systems",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2021", 7, "Differentiate GPP , ASIP and Single purpose processor with respect to embedded system using specific application"),
            ("Summer 2023", 4, "Describe an embedded processor as (i) GPP (ii) ASIP (iii) Single purpose processor.")
        ]
    },
    "1.5": {
        "text": "List down the components available on SoC and describe them with a neat diagram.",
        "chapter": "1. Introduction to Embedded Systems",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2021", 7, "List down the components available on SoC and describe them with a neat diagram.")
        ]
    },
    "1.6": {
        "text": "Describe the use of FPGA and SoC to design Embedded system.",
        "chapter": "1. Introduction to Embedded Systems",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2025", 4, "Describe use of FPGA and SoC to design Embedded system.")
        ]
    },
    "1.7": {
        "text": "Discuss the design process in embedded systems with examples.",
        "chapter": "1. Introduction to Embedded Systems",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2024", 7, "Discuss the design process in embedded systems with examples.")
        ]
    },
    "1.8": {
        "text": "Describe criteria to choose microcontroller for designing embedded system.",
        "chapter": "1. Introduction to Embedded Systems",
        "difficulty": "Easy",
        "raw_matches": [
            ("Winter 2025", 3, "Describe criteria to choose microcontroller for designing embedded system.")
        ]
    },
    "1.9": {
        "text": "“Increasing the frequency of an embedded system increases the power dissipation” Justify the statement.",
        "chapter": "1. Introduction to Embedded Systems",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2021", 3, "“Increasing the frequency of an embedded system increases the power dissipation” Justify the statement")
        ]
    },
    "1.10": {
        "text": "Give classification of Embedded systems.",
        "chapter": "1. Introduction to Embedded Systems",
        "difficulty": "Easy",
        "raw_matches": [
            ("Summer 2024", 3, "Give classification of Embedded systems.")
        ]
    },
    "2.1": {
        "text": "Describe Watchdog Timer, Real Time Clock (RTC) and Brown Out Reset (BOR) with examples.",
        "chapter": "2. Device and Communication Buses",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2021", 3, "Define RTC and Watchdog Timer"),
            ("Summer 2022", 4, "Describe Watch Dog Timer and Brown Out Reset with example."),
            ("Winter 2023", 4, "Describe use of RTC and WDT in Embedded system."),
            ("Summer 2025", 3, "What is watch dog Timer? Explain its function in brief."),
            ("Summer 2025", 4, "How does Brown Out Reset work in microcontroller?"),
            ("Winter 2025", 4, "Describe how WDT can used to solve unavoidable software loop."),
            ("Winter 2022", 7, "Describe the features available with Watch Dog Timer along with its requirements in embedded system design.")
        ]
    },
    "2.2": {
        "text": "Compare Wi-Fi, Bluetooth and Zigbee protocols and their features in wireless/mobile communication.",
        "chapter": "2. Device and Communication Buses",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2021", 4, "Explain the features associated with Bluetooth and Zigbee devices."),
            ("Summer 2022", 7, "Compare Wi-Fi, Blue-tooth and Zigbee algorithm"),
            ("Summer 2023", 3, "Describe the features associated with Bluetooth and Zigbee protocols used in wireless and mobile systems."),
            ("Winter 2023", 7, "Describe and compare Wi-fi and Bluetooth protocol."),
            ("Summer 2024", 3, "List the down features of Bluetooth protocol."),
            ("Summer 2024", 7, "Compare: IrDA, Wi-Fi and ZigBee."),
            ("Summer 2025", 7, "List down wireless communication protocol and explain any one in detail."),
            ("Winter 2022", 7, "List and explain the protocols used for wireless and mobile system communication."),
            ("Winter 2024", 7, "Explain Wireless Communication protocols and their significance in embedded systems.")
        ]
    },
    "2.3": {
        "text": "Compare the advantages and disadvantages of data transfers using serial and parallel ports, and describe SPI protocol.",
        "chapter": "2. Device and Communication Buses",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 7, "Compare the advantages and disadvantages of data transfers using serial and parallel ports devices. Describe SPI protocol."),
            ("Winter 2022", 4, "Explain SPI bus protocol to establish serial communication between a processor and a device.")
        ]
    },
    "2.4": {
        "text": "Differentiate between serial and parallel communication, and explain USART protocol in brief.",
        "chapter": "2. Device and Communication Buses",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2023", 7, "Differentiate between serial and parallel communication. Explain USART protocol in brief."),
            ("Winter 2025", 3, "Compare Synchronous and Asynchronous serial communication method."),
            ("Winter 2023", 3, "Describe Synchronous, Iso-synchronous, and Asynchronous communication."),
            ("Winter 2024", 4, "Compare and contrast various Serial Communication protocols.")
        ]
    },
    "2.5": {
        "text": "List the features associated with AHB and ASB Buses.",
        "chapter": "2. Device and Communication Buses",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2023", 4, "List the features associated with AHB and ASB Buses.")
        ]
    },
    "2.6": {
        "text": "Explain I2C and CAN bus protocols in brief.",
        "chapter": "2. Device and Communication Buses",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2023", 7, "Explain I2C and CAN bus protocol in brief."),
            ("Winter 2023", 7, "Describe CAN bus protocol."),
            ("Winter 2025", 7, "Describe CAN bus protocol with merits and demerits."),
            ("Winter 2025", 7, "Compare UART, SPI, I2C, USB protocol for different criteria."),
            ("Winter 2023", 7, "Compare UART, I2C, SPI protocol. Give advantage of each protocol over other protocol.")
        ]
    },
    "2.7": {
        "text": "Explain UART protocol in Serial Communication.",
        "chapter": "2. Device and Communication Buses",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2021", 4, "Explain UART protocol in Serial Communication.")
        ]
    },
    "2.8": {
        "text": "Explain USB Protocol in detail.",
        "chapter": "2. Device and Communication Buses",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2024", 7, "Explain USB Protocol in detail.")
        ]
    },
    "2.9": {
        "text": "Explain the working of the Secure Digital Input Output (SDIO) protocol.",
        "chapter": "2. Device and Communication Buses",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2025", 7, "Explain the working of the Secure Digital Input Output (SDIO) protocol.")
        ]
    },
    "2.10": {
        "text": "Explain the working of Spy-Bi-Wire serial communication protocol.",
        "chapter": "2. Device and Communication Buses",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2025", 7, "Explain the working of Spy-Bi-Wire serial communication protocol.")
        ]
    },
    "2.11": {
        "text": "Discuss the features and applications of Parallel Communication protocols.",
        "chapter": "2. Device and Communication Buses",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2024", 7, "Discuss the features and applications of Parallel Communication protocols.")
        ]
    },
    "2.12": {
        "text": "Explain the role of Timer and Counting Devices in embedded systems.",
        "chapter": "2. Device and Communication Buses",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2024", 3, "Explain the role of Timer and Counting Devices in embedded systems.")
        ]
    },
    "2.13": {
        "text": "Describe AMBA protocol and its variants.",
        "chapter": "2. Device and Communication Buses",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2025", 7, "Describe AMBA protocol and its variant.")
        ]
    },
    "3.1": {
        "text": "Describe the busy wait approach and interrupt mechanism for accessing I/O.",
        "chapter": "3. Device Drivers and Interrupt Services Mechanism",
        "difficulty": "Easy",
        "raw_matches": [
            ("Summer 2022", 3, "Describe busy wait approach for accessing IO."),
            ("Summer 2022", 3, "Describe interrupt mechanism for accessing IO."),
            ("Winter 2023", 3, "Describe polled based IO and interrupt based IO.")
        ]
    },
    "3.2": {
        "text": "Describe Direct Memory Access (DMA) and the operation of a DMA controller.",
        "chapter": "3. Device Drivers and Interrupt Services Mechanism",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2021", 7, "Explain DMA Controller"),
            ("Summer 2022", 7, "Describe Direct Memory Access."),
            ("Winter 2022", 7, "What is DMA? Using diagram show the operation of a DMA controller."),
            ("Winter 2023", 4, "Sketch diagram to interface DMA with microprocessor or microcontroller."),
            ("Winter 2024", 4, "Explain the Direct Memory Access (DMA) concept."),
            ("Summer 2025", 4, "Sketch diagram to interface DMA with microprocessor or microcontroller"),
            ("Winter 2025", 4, "Describe use of DMA in embedded system design for data transfer form IO device to memory.")
        ]
    },
    "3.3": {
        "text": "Explain different types of interrupt sources.",
        "chapter": "3. Device Drivers and Interrupt Services Mechanism",
        "difficulty": "Easy",
        "raw_matches": [
            ("Summer 2023", 3, "Explain different types of interrupt sources.")
        ]
    },
    "3.4": {
        "text": "Explain the concept of Interrupt Service Routine (ISR).",
        "chapter": "3. Device Drivers and Interrupt Services Mechanism",
        "difficulty": "Easy",
        "raw_matches": [
            ("Winter 2022", 4, "Explain concept of interrupt service routine."),
            ("Summer 2025", 4, "Explain concept of interrupt service routine."),
            ("Winter 2024", 3, "What is an Interrupt Service Routine (ISR)?")
        ]
    },
    "3.5": {
        "text": "What is a Device Driver and explain the role of interrupts in device driver programming.",
        "chapter": "3. Device Drivers and Interrupt Services Mechanism",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2021", 7, "Explain Device driver mechanism in an embedded system."),
            ("Summer 2023", 7, "What is Device driver? Explain role of Interrupt in Device driver programming."),
            ("Winter 2022", 7, "What is a device driver? What are its requirements? Describe the information required for writing a device driver."),
            ("Winter 2023", 4, "Describe device driver used in embedded system."),
            ("Summer 2024", 4, "Describe the information required for writing a device driver."),
            ("Winter 2024", 7, "Explain the role of Device Driver Programming in embedded systems."),
            ("Winter 2025", 4, "Describe types of device driver with examples.")
        ]
    },
    "3.6": {
        "text": "List down the steps executed before handling an Interrupt in an embedded system.",
        "chapter": "3. Device Drivers and Interrupt Services Mechanism",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2021", 3, "List down the steps executed before handling an Interrupt in an embedded system."),
            ("Summer 2024", 3, "List down the steps executed before handling an Interrupt in an embedded system.")
        ]
    },
    "3.7": {
        "text": "Differentiate between Function and ISR.",
        "chapter": "3. Device Drivers and Interrupt Services Mechanism",
        "difficulty": "Easy",
        "raw_matches": [
            ("Winter 2021", 3, "Differentiate : Function and ISR")
        ]
    },
    "3.8": {
        "text": "Describe the classification of processor interrupt service mechanisms.",
        "chapter": "3. Device Drivers and Interrupt Services Mechanism",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2024", 7, "Describe the classification of processor interrupt service mechanisms")
        ]
    },
    "3.9": {
        "text": "Discuss the context-switching mechanism in the presence of multiple interrupts.",
        "chapter": "3. Device Drivers and Interrupt Services Mechanism",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2024", 3, "Discuss the context-switching mechanism in the presence of multiple interrupts."),
            ("Summer 2025", 7, "What is context switching? Explain context switching on interrupts.")
        ]
    },
    "3.10": {
        "text": "Define Interrupt Deadline. How does an embedded software designer solve the interrupt deadline problem?",
        "chapter": "3. Device Drivers and Interrupt Services Mechanism",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2025", 3, "Define Interrupt Deadline. How embedded software designer solve interrupt deadline problem?")
        ]
    },
    "3.11": {
        "text": "Enumerate various I/O types of an embedded system and explain them with examples.",
        "chapter": "3. Device Drivers and Interrupt Services Mechanism",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2021", 7, "Enumerate various I/O types of an embedded system and explain them with examples.")
        ]
    },
    "3.12": {
        "text": "Explain Interrupt Latency and Interrupt Service Deadline, and describe the parameters governing their values.",
        "chapter": "3. Device Drivers and Interrupt Services Mechanism",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2021", 3, "Explain Interrupt latency and deadline."),
            ("Winter 2022", 3, "Define Interrupt Latency and Interrupt Service Deadline. Describe the parameters that govern their values."),
            ("Summer 2023", 4, "Define Interrupt Latency and Interrupt Service Deadline. Describe the parameters that govern their values"),
            ("Winter 2023", 3, "Define interrupt, interrupt latency, Task Deadline."),
            ("Summer 2024", 7, "Explain following: 1. Context and the Periods for Context Switching, 2. Interrupt Latency and Deadline"),
            ("Winter 2024", 4, "Describe the concept of Interrupt Latency and its impact."),
            ("Winter 2025", 3, "Define interrupt latency. Describe equations to find interrupt latency.")
        ]
    },
    "4.1": {
        "text": "Differentiate between Process and Thread.",
        "chapter": "4. Inter-process Communication",
        "difficulty": "Easy",
        "raw_matches": [
            ("Summer 2022", 4, "Differentiate : Process and Thread"),
            ("Summer 2024", 4, "Give comparison between process and thread."),
            ("Winter 2023", 4, "Compare Process, Thread and Function.")
        ]
    },
    "4.2": {
        "text": "Compare process, task and thread with an appropriate example.",
        "chapter": "4. Inter-process Communication",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2023", 7, "Compare process, task and thread with an appropriate example. Explain multithreading mechanism in context of the display process of desktop systems."),
            ("Winter 2022", 7, "Compare process, task and thread with appropriate example. Also explain multithreading mechanism in context of display process of mobile phone.")
        ]
    },
    "4.3": {
        "text": "Differentiate between a Task, a Function and an Interrupt Service Routine.",
        "chapter": "4. Inter-process Communication",
        "difficulty": "Easy",
        "raw_matches": [
            ("Winter 2022", 4, "State the differences between a Task, a Function and an Interrupt Service Routine.")
        ]
    },
    "4.4": {
        "text": "Describe the shared data problem with an example and its solutions.",
        "chapter": "4. Inter-process Communication",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 7, "Describe shared data problem with example. How to solve this issue?"),
            ("Winter 2022", 3, "Discuss shared data problems and give solutions to such problems."),
            ("Winter 2023", 7, "Describe shared data problem with example."),
            ("Winter 2024", 3, "Describe shared data management in multi-threaded applications.")
        ]
    },
    "4.5": {
        "text": "Describe Mailbox, Pipe, Socket, and RPC functions used for Inter-Process Communication (IPC).",
        "chapter": "4. Inter-process Communication",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 4, "Describe Mailbox function for IPC."),
            ("Summer 2023", 7, "Give advantages, disadvantages and uses of mailbox, pipe and socket functions in interprocess communication."),
            ("Summer 2024", 3, "Explain: 1.RPC function 2.Socket function."),
            ("Winter 2024", 4, "Discuss various IPC mechanisms such as message queues and sockets."),
            ("Winter 2024", 4, "Explain the use of Pipe Functions in IPC."),
            ("Winter 2025", 7, "Describe Mailbox functions and RPC used for inter-process communication.")
        ]
    },
    "4.6": {
        "text": "Describe priority inversion and deadlock conditions, and how to solve these issues.",
        "chapter": "4. Inter-process Communication",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 7, "Describe Priority inversion and Deadlock condition. How to solve these issues?"),
            ("Winter 2023", 7, "Describe dead-lock condition with example in embedded system. How to come out of dead-lock condition?"),
            ("Winter 2025", 7, "Describe priority inversion problem. How to solve it?")
        ]
    },
    "4.7": {
        "text": "What is a Semaphore? Explain where it can be utilized along with its advantages and disadvantages.",
        "chapter": "4. Inter-process Communication",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2021", 4, "Explain Semaphores"),
            ("Summer 2023", 4, "What is Semaphore? Explain where Semaphore can be utilized?"),
            ("Winter 2022", 4, "Discuss use of a semaphore as an event signaling or notifying variable in brief."),
            ("Summer 2024", 7, "What is Semaphore? Write down advantages and disadvantages of semaphore."),
            ("Winter 2024", 3, "Explain the significance of semaphores in inter-process communication."),
            ("Winter 2025", 7, "Describe different types of semaphore and its related OS level functions. How it can be used as resource handling mechanism?"),
            ("Summer 2025", 7, "Describe the main problem with semaphores and its limitation.")
        ]
    },
    "4.8": {
        "text": "Differentiate between Binary Semaphore and Mutex.",
        "chapter": "4. Inter-process Communication",
        "difficulty": "Easy",
        "raw_matches": [
            ("Summer 2022", 4, "Differentiate : Binary Semaphore and Mutex"),
            ("Winter 2023", 4, "Describe PV Semaphore with example."),
            ("Summer 2025", 4, "What do you mean by Mutex? Also explain P and V semaphore with appropriate example."),
            ("Winter 2022", 7, "What do you mean by Mutex. Also explain P and V semaphore with appropriate example.")
        ]
    },
    "4.9": {
        "text": "Define Process Control Block (PCB) and list the data fields included in it.",
        "chapter": "4. Inter-process Communication",
        "difficulty": "Easy",
        "raw_matches": [
            ("Winter 2021", 4, "What is Process Control Block? What are the fields included in PCB ?"),
            ("Summer 2022", 3, "Define : Process Control Block. Which data is stored in PCB?"),
            ("Summer 2023", 3, "Define: Process Control Block. Which data is stored in PCB?")
        ]
    },
    "4.10": {
        "text": "Describe Critical Section and how to achieve this functionality in programming.",
        "chapter": "4. Inter-process Communication",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 4, "Describe Critical Section. How to achieve this functionality in programming.")
        ]
    },
    "4.11": {
        "text": "What is Inter-Process Communication (IPC)? List down and explain methods of IPC in brief.",
        "chapter": "4. Inter-process Communication",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2021", 4, "Write a note on IPC."),
            ("Summer 2024", 4, "What is inter process communication? How it is done?"),
            ("Summer 2025", 7, "What is inter process communication (IPC)? List down and explain methods of IPC in brief.")
        ]
    },
    "4.12": {
        "text": "Discuss the role of signal functions in process communication.",
        "chapter": "4. Inter-process Communication",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2024", 7, "Discuss the role of signal functions in process communication.")
        ]
    },
    "4.13": {
        "text": "Describe Lock, Unlock and Spin-lock mechanisms used for Inter-Process Communication.",
        "chapter": "4. Inter-process Communication",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2025", 7, "Describe Lock, Unlock and Spin-lock mechanism used for inter-process communication.")
        ]
    },
    "4.14": {
        "text": "Compare the characteristics of tasks and ISRs.",
        "chapter": "4. Inter-process Communication",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2024", 7, "Compare the characteristics of tasks and ISRs.")
        ]
    },
    "4.15": {
        "text": "Differentiate between Multiprocessing and Multithreading.",
        "chapter": "4. Inter-process Communication",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2025", 7, "Give difference between Multiprocessing and Multithreading.")
        ]
    },
    "5.1": {
        "text": "Define RTOS. Enlist types of RTOS with examples.",
        "chapter": "5. Introduction to OS and Real Time Operating System",
        "difficulty": "Easy",
        "raw_matches": [
            ("Winter 2021", 4, "What is RTOS ? Describe types of RTOS with two examples."),
            ("Summer 2022", 3, "Define RTOS. Enlist types of RTOS with examples."),
            ("Summer 2023", 3, "What is RTOS ? Describe types of RTOS with two examples."),
            ("Winter 2023", 4, "Define RTOS. Describe its type with example."),
            ("Winter 2025", 3, "Define RTOS. Describe its type with examples.")
        ]
    },
    "5.2": {
        "text": "Define and explain different Benchmarking parameters for an RTOS.",
        "chapter": "5. Introduction to OS and Real Time Operating System",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2023", 4, "Define and explain different Benchmarking parameters for an RTOS."),
            ("Summer 2025", 4, "What is meant by benchmarking Real time operating system (RTOS)? Why it is required?")
        ]
    },
    "5.3": {
        "text": "Describe the differences between Hard Real Time and Soft Real Time System with examples.",
        "chapter": "5. Introduction to OS and Real Time Operating System",
        "difficulty": "Easy",
        "raw_matches": [
            ("Summer 2023", 4, "Describe the differences between Hard Real Time and Soft Real Time System with an example of each one."),
            ("Winter 2022", 3, "Compare hard real time and soft real time.")
        ]
    },
    "5.4": {
        "text": "Write down the key features and services of an Operating System.",
        "chapter": "5. Introduction to OS and Real Time Operating System",
        "difficulty": "Easy",
        "raw_matches": [
            ("Summer 2024", 3, "Write down the features of an operating system."),
            ("Winter 2024", 3, "Define the key features of an Operating System."),
            ("Summer 2025", 3, "List down features of an operating system.")
        ]
    },
    "5.5": {
        "text": "Write down advantages and disadvantages of RTOS.",
        "chapter": "5. Introduction to OS and Real Time Operating System",
        "difficulty": "Easy",
        "raw_matches": [
            ("Summer 2024", 4, "Write down advantages and disadvantages of RTOS.")
        ]
    },
    "5.6": {
        "text": "Describe memory and file management in RTOS.",
        "chapter": "5. Introduction to OS and Real Time Operating System",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2021", 7, "Describe memory and file management in RTOS"),
            ("Winter 2022", 4, "Write short note on memory management."),
            ("Winter 2022", 7, "Describe the significance of File and I/O management along with supported functions in RTOS"),
            ("Summer 2023", 7, "Explain device, file and I/O management in RTOS.")
        ]
    },
    "5.7": {
        "text": "Explain task scheduling in RTOS.",
        "chapter": "5. Introduction to OS and Real Time Operating System",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2021", 4, "Explain task scheduling in RTOS")
        ]
    },
    "5.8": {
        "text": "What do you understand by Interrupt Service Thread? Explain its usage with an example in RTOS based systems.",
        "chapter": "5. Introduction to OS and Real Time Operating System",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2022", 4, "What do you understand by Interrupt Service Thread? Explain its usage with an example in RTOS based systems.")
        ]
    },
    "5.9": {
        "text": "List down the services provided by RTOS.",
        "chapter": "5. Introduction to OS and Real Time Operating System",
        "difficulty": "Easy",
        "raw_matches": [
            ("Winter 2021", 3, "List down the services provided by RTOS."),
            ("Summer 2024", 3, "List down the services provided by RTOS.")
        ]
    },
    "6.1": {
        "text": "Describe the Earliest Deadline First (EDF) mechanism with an example.",
        "chapter": "6. Software architectures and Real Time Task Scheduling",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 3, "Describe Earliest Deadline First Mechanism with example."),
            ("Winter 2023", 7, "Describe Earlier Deadline First (EDF) and rate-monotonic scheduling mechanism."),
            ("Summer 2024", 4, "Explain Earliest-Deadline First Scheduling."),
            ("Winter 2025", 4, "Describe Earlier Deadline First (EDF) scheduling mechanism."),
            ("Summer 2025", 3, "Describe Earliest Deadline First Mechanism with example.")
        ]
    },
    "6.2": {
        "text": "Describe the Round-robin with interrupt mechanism for embedded software.",
        "chapter": "6. Software architectures and Real Time Task Scheduling",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 7, "Describe Round-robin with interrupt mechanism for embedded software."),
            ("Summer 2024", 7, "Describe Round-robin with interrupt mechanism for embedded software."),
            ("Winter 2023", 7, "Describe Round-robin with interrupt scheduling with example."),
            ("Summer 2025", 3, "Describe Round Robin with Interrupts.")
        ]
    },
    "6.3": {
        "text": "Describe and compare co-operative and pre-emptive scheduling mechanisms.",
        "chapter": "6. Software architectures and Real Time Task Scheduling",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 7, "Describe co-operative and pre-emptive scheduling mechanism."),
            ("Summer 2023", 3, "Explain the differences between Preemptive & Non-Preemptive scheduling policies."),
            ("Winter 2023", 3, "Enlist co-operative scheduling mechanism"),
            ("Winter 2023", 3, "Enlist pre-emptive scheduling mechanism."),
            ("Summer 2024", 7, "What is multitasking? Differentiate between Preemptive and Cooperative Multitasking."),
            ("Winter 2024", 4, "Compare cooperative and preemptive multitasking."),
            ("Winter 2025", 3, "Compare pre-emptive and co-operative scheduling mechanism.")
        ]
    },
    "6.4": {
        "text": "Explain process context switching and thread context switching in detail.",
        "chapter": "6. Software architectures and Real Time Task Scheduling",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2023", 7, "Explain process context switching and thread context switching in detail. Justify “threads are lightweight processes”.")
        ]
    },
    "6.5": {
        "text": "Differentiate between Clock-driven and Event-driven Scheduling.",
        "chapter": "6. Software architectures and Real Time Task Scheduling",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2024", 4, "Differentiate Clock driven and Event driven scheduling."),
            ("Summer 2025", 7, "Differentiate between Clock-driven and Event-driven Scheduling."),
            ("Winter 2024", 4, "Explain the difference between clock-driven and event-driven scheduling.")
        ]
    },
    "6.6": {
        "text": "Write down various types of states of tasks and explain them.",
        "chapter": "6. Software architectures and Real Time Task Scheduling",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2024", 7, "Write down various types of states of tasks? Explain them.")
        ]
    },
    "6.7": {
        "text": "Explain Rate-monotonic scheduling.",
        "chapter": "6. Software architectures and Real Time Task Scheduling",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2025", 4, "Explain Rate-monotonic scheduling."),
            ("Winter 2024", 7, "Compare Rate-Monotonic Scheduling and Earliest-Deadline First Scheduling.")
        ]
    },
    "6.8": {
        "text": "Describe Function Queue Scheduling mechanism.",
        "chapter": "6. Software architectures and Real Time Task Scheduling",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2025", 4, "Describe Function Queue Scheduling mechanism.")
        ]
    },
    "6.9": {
        "text": "What is a Scheduler? Explain any one scheduling policies.",
        "chapter": "6. Software architectures and Real Time Task Scheduling",
        "difficulty": "Easy",
        "raw_matches": [
            ("Winter 2022", 3, "What is a Scheduler? Explain any one scheduling policies.")
        ]
    },
    "6.10": {
        "text": "Name all the RTOS task scheduling models. Describe any one in brief.",
        "chapter": "6. Software architectures and Real Time Task Scheduling",
        "difficulty": "Easy",
        "raw_matches": [
            ("Winter 2022", 3, "Name all the RTOS task scheduling models. Describe any one in brief.")
        ]
    },
    "7.1": {
        "text": "Sketch and describe the block diagram and basic architecture of MSP430 and its registers.",
        "chapter": "7. MSP430 (Case Study)",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 3, "Sketch and Describe block diagram of MSP430"),
            ("Winter 2022", 4, "Draw and explain the basic architecture and block diagram of MSP430."),
            ("Winter 2025", 3, "Describe MSP430 block diagram and CPU registers.")
        ]
    },
    "7.2": {
        "text": "Describe the low-power features and modes of MSP430 microcontrollers.",
        "chapter": "7. MSP430 (Case Study)",
        "difficulty": "Easy",
        "raw_matches": [
            ("Winter 2021", 3, "Describe low power mode of MSP30."),
            ("Summer 2022", 4, "Describe low-power modes of MSP430."),
            ("Summer 2024", 3, "Describe low power mode of MSP430."),
            ("Winter 2024", 7, "Discuss the low-power features of MSP430 microcontrollers."),
            ("Winter 2025", 4, "Describe how to achieve low-power modes in MSP430.")
        ]
    },
    "7.3": {
        "text": "Sketch interfacing diagram and write C-code to count switch presses using interrupts with MSP430.",
        "chapter": "7. MSP430 (Case Study)",
        "difficulty": "Hard",
        "raw_matches": [
            ("Summer 2022", 7, "Common cathode seven-segment and push-button is connected with MSP430. Sketch interfacing diagram and write C-code to count number of times switch is pressed (Use interrupt subroutine when switch is connected)")
        ]
    },
    "7.4": {
        "text": "Describe the multiplexing scheme in MSP430 processor for the port pins.",
        "chapter": "7. MSP430 (Case Study)",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 3, "Describe multiplexing scheme in MSP430 processor for the port pins."),
            ("Winter 2022", 3, "Explain the multiplexing scheme in MSP430 processor for the port pins."),
            ("Winter 2023", 3, "Describe multiplexing scheme of MSP430 pins.")
        ]
    },
    "7.5": {
        "text": "Describe the clocking system and various sources of clock in MSP430 processor.",
        "chapter": "7. MSP430 (Case Study)",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2021", 4, "Describe the various sources of clock in MSP430 processor"),
            ("Summer 2022", 4, "Describe clocking system of MSP430."),
            ("Summer 2023", 4, "Describe the four sources of clock in MSP430 processor"),
            ("Winter 2022", 4, "Explain the clocking system of MSP430."),
            ("Summer 2024", 4, "Describe the various sources of clock in MSP430 processor."),
            ("Summer 2025", 3, "Describe the four sources of clock in MSP430 processor."),
            ("Winter 2025", 4, "Describe clocking system in MSP430. Is it possible to drive all peripherals of MSP430 at master clock speed? Justify your answer.")
        ]
    },
    "7.6": {
        "text": "Describe MSP430 timer modes available for Timer-A and write a C-program to generate square wave on port pin P1.0 using Timer-A.",
        "chapter": "7. MSP430 (Case Study)",
        "difficulty": "Hard",
        "raw_matches": [
            ("Summer 2022", 7, "Describe MSP430 timer modes available for Timer-A. Write C-Program for MSP430 to generate 1KHz square wave on pin P1.0 using Timer-A."),
            ("Winter 2022", 7, "Explain a Timer module of MSP430 with various modes of operation associated with it."),
            ("Winter 2022", 7, "Describe the interrupt feature associated with Timer in MSP430."),
            ("Winter 2023", 7, "Write a C-program to generate square wave of 100Hz using timer-A. Assume SMCLK = 1MHz")
        ]
    },
    "7.7": {
        "text": "Explain the function of Watchdog timer in MSP430 processor.",
        "chapter": "7. MSP430 (Case Study)",
        "difficulty": "Easy",
        "raw_matches": [
            ("Summer 2023", 3, "Explain the function of Watchdog timer in MSP430 processor."),
            ("Summer 2024", 3, "Discuss watch dog timer of MSP430.")
        ]
    },
    "7.8": {
        "text": "Describe reset conditions of MSP430: BOR, POR and PUC.",
        "chapter": "7. MSP430 (Case Study)",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2023", 3, "Describe POR, PUC and BOR for MSP430."),
            ("Winter 2023", 4, "Describe reset condition of MSP430: BOR, POR and PUC")
        ]
    },
    "7.9": {
        "text": "Explain interrupt handling process in MSP430.",
        "chapter": "7. MSP430 (Case Study)",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2023", 7, "Explain interrupt handling process in MSP430.")
        ]
    },
    "7.10": {
        "text": "Explain how the timers of MSP430 can be configured for PWM generation.",
        "chapter": "7. MSP430 (Case Study)",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2021", 7, "Explain how the timers of MSP430 can be configured for PWM generation."),
            ("Summer 2023", 7, "Explain the use of timer for generating Pulse Width Modulated waveform using MSP430."),
            ("Summer 2024", 7, "Explain how the timers of MSP430 can be configured for PWM generation.")
        ]
    },
    "7.11": {
        "text": "List down various registers of MSP430 processor with their functions.",
        "chapter": "7. MSP430 (Case Study)",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2024", 7, "List down various registers of MSP430 processor with their functions.")
        ]
    },
    "7.12": {
        "text": "Describe MSP430 USCI module and its modes.",
        "chapter": "7. MSP430 (Case Study)",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2023", 3, "Describe MSP430 USCI module and its modes."),
            ("Summer 2025", 3, "Describe MSP430 USCI module and its modes.")
        ]
    },
    "7.13": {
        "text": "Explain the special features associated with GPIO port pins in MSP430 other than simple digital input output port pin characteristics.",
        "chapter": "7. MSP430 (Case Study)",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2022", 3, "Explain the special features associated with GPIO port pins in MSP430 other than simple digital input output port pin characteristics."),
            ("Summer 2025", 3, "Explain the special features associated with GPIO port pins in MSP430 other than simple digital input output port pin characteristics.")
        ]
    },
    "7.14": {
        "text": "Draw interfacing diagram to interface 8 LEDs with MSP430 and write C-code to turn them ON in ring counter fashion.",
        "chapter": "7. MSP430 (Case Study)",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2023", 7, "Sketch interfacing diagram to interface 8 LEDs with MSP430. Turn-ON LEDs in ring counter fashion."),
            ("Summer 2025", 7, "Draw interfacing diagram to interface 8 LEDs with MSP430. Turn-ON LEDs in ring counter fashion.")
        ]
    },
    "7.15": {
        "text": "Write a C code to display HELLO on common anode seven segment LED interfaced with GPIO pins of MSP430. Show necessary diagram.",
        "chapter": "7. MSP430 (Case Study)",
        "difficulty": "Hard",
        "raw_matches": [
            ("Winter 2021", 7, "Write a C code to display HELLO on common anode seven segment LED interfaced with GPIO pins of MSP430. Show necessary diagram.")
        ]
    },
    "7.16": {
        "text": "MSP430 is having an orthogonal CPU architecture supported with RISC features. Justify the statement.",
        "chapter": "7. MSP430 (Case Study)",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2023", 4, "MSP430 is having an orthogonal CPU architecture supported with RISC features. – Justify the statement."),
            ("Summer 2025", 4, "MSP430 is having an orthogonal CPU architecture supported with RISC features. – Justify the statement.")
        ]
    },
    "7.17": {
        "text": "Enlist features of ADC10 block in MSP430, and explain why CPU temperature and power supply is converted in digital.",
        "chapter": "7. MSP430 (Case Study)",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2025", 3, "Enlist features of ADC10 block in MSP430. For MSP430, Why CPU temperature and power supply is converted in digital?")
        ]
    },
    "7.18": {
        "text": "Sketch interfacing diagram to interface one switch at P1.3 and two LEDs at P1.0 and P1.6 with MSP430 board, and write C-program to control them.",
        "chapter": "7. MSP430 (Case Study)",
        "difficulty": "Hard",
        "raw_matches": [
            ("Winter 2025", 7, "Sketch interfacing diagram to interface one switch at P1.3 and two LEDs at P1.0 and P1.6 with MSP430 board. Write C-program to do following")
        ]
    },
    "7.19": {
        "text": "Write a MSP430 C-program to transmit “GTU EXAM” continuously using UART at 9600 baudrate. Assume SMCLK = 1MHz.",
        "chapter": "7. MSP430 (Case Study)",
        "difficulty": "Hard",
        "raw_matches": [
            ("Winter 2025", 7, "Write a MSP430 C-program to transmit “GTU EXAM” continuously using UART at 9600 baudrate. Assume SMCLK = 1MHz")
        ]
    },
    "7.20": {
        "text": "List the features of MSP430 microcontroller.",
        "chapter": "7. MSP430 (Case Study)",
        "difficulty": "Easy",
        "raw_matches": [
            ("Winter 2021", 3, "List the features of MSP430 microcontroller")
        ]
    },
    "7.21": {
        "text": "What are the key features of the MSP430 architecture?",
        "chapter": "7. MSP430 (Case Study)",
        "difficulty": "Easy",
        "raw_matches": [
            ("Winter 2024", 3, "What are the key features of the MSP430 architecture?")
        ]
    }
}

# ==============================================================================
# ANTENNAS AND PROPAGATION DATA DEFINITIONS
# ==============================================================================

ap_unique_questions = {
    "1.1": {
        "text": "Define the antenna term in different ways, and compare antenna with transmission line.",
        "chapter": "1. Basic antenna concepts",
        "difficulty": "Easy",
        "raw_matches": [
            ("Summer 2023", 3, "Define the antenna term in different ways."),
            ("Winter 2024", 3, "Compare antenna with transmission line.")
        ]
    },
    "1.2": {
        "text": "Draw and explain different parts of radiation pattern.",
        "chapter": "1. Basic antenna concepts",
        "difficulty": "Easy",
        "raw_matches": [
            ("Summer 2023", 3, "Draw and explain different parts of radiation pattern."),
            ("Winter 2024", 3, "Draw and explain different parts of radiation pattern.")
        ]
    },
    "1.3": {
        "text": "List down different types of antennas and explain them.",
        "chapter": "1. Basic antenna concepts",
        "difficulty": "Easy",
        "raw_matches": [
            ("Summer 2025", 7, "List down different types of antennas and explain any 2 with necessary figures."),
            ("Winter 2025", 4, "Enlist different types of antenna based on radiation pattern."),
            ("Winter 2022", 4, "List out the different antennas with suitable figures.")
        ]
    },
    "1.4": {
        "text": "Explain different types of antenna apertures.",
        "chapter": "1. Basic antenna concepts",
        "difficulty": "Easy",
        "raw_matches": [
            ("Summer 2024", 3, "Explain different types of antenna apertures.")
        ]
    },
    "2.1": {
        "text": "Obtain the ratio of E_theta and H_phi field components of a current element in free space with derivations using Maxwell's equations.",
        "chapter": "2. Radiation of Electric dipole",
        "difficulty": "Hard",
        "raw_matches": [
            ("Winter 2021", 7, "Derive the equations of E and H for an electric dipole."),
            ("Summer 2022", 7, "Obtain the ratio of Eθ and HФ field components of a current element at a distance point in free space with necessary derivations using Maxwell's equation"),
            ("Summer 2024", 7, "Obtain the ratio of Eθ and HФ field components of a current element at a distance point in free space with necessary derivations using Maxwell's equation."),
            ("Winter 2022", 7, "Deduce an expression for the field components of a current element at a distant point in free space."),
            ("Winter 2022", 4, "Discuss the power radiated by a current element.")
        ]
    },
    "2.2": {
        "text": "Derive an expression for electric and magnetic components of a short dipole antenna if the spherical system is defined in r, theta and phi.",
        "chapter": "2. Radiation of Electric dipole",
        "difficulty": "Hard",
        "raw_matches": [
            ("Summer 2023", 7, "Derive an expression for electric and magnetic components of a short dipole antenna if the spherical system is defined in r, θ and ϕ."),
            ("Winter 2024", 7, "Derive an expressions for electric and magnetic components of a short dipole antenna if the spherical system is defined in r, θ and ϕ.")
        ]
    },
    "2.3": {
        "text": "Derive the expression for the radiation resistance of half-wave dipole and prove that it is 73 Ohm.",
        "chapter": "2. Radiation of Electric dipole",
        "difficulty": "Hard",
        "raw_matches": [
            ("Summer 2024", 7, "Derive the expression for the radiation resistance of half-wave dipole."),
            ("Winter 2025", 7, "Derive the far field components of a half-wave dipole antenna."),
            ("Winter 2021", 7, "Show that the radiation resistance of a dipole antenna is 73Ω."),
            ("Winter 2022", 7, "Discuss radiation field of a half wave dipole antenna with necessary expressions."),
            ("Winter 2024", 7, "Derive an expression for radiation resistance of short dipole for far-field region. Prove that radiation resistance of half wave dipole antenna is 73 Ω.")
        ]
    },
    "2.4": {
        "text": "Derive the far field components and radiation resistance of a small circular loop.",
        "chapter": "2. Radiation of Electric dipole",
        "difficulty": "Hard",
        "raw_matches": [
            ("Summer 2024", 7, "Derive the far field components of a small circular loop with radius ‘a' and with a uniform phase current."),
            ("Winter 2021", 7, "Obtain the expression for the far field of circular loop."),
            ("Winter 2025", 7, "Derive the field components of a small loop antenna."),
            ("Summer 2025", 7, "Explain about loop antenna. Explain the working principle of small loop antenna with necessary equations"),
            ("Winter 2024", 7, "Give an expression of radiation resistance of a small loop.")
        ]
    },
    "2.5": {
        "text": "Derive the far field components of a monopole antenna.",
        "chapter": "2. Radiation of Electric dipole",
        "difficulty": "Hard",
        "raw_matches": [
            ("Winter 2025", 7, "Derive the far field components of a monopole antenna.")
        ]
    },
    "2.6": {
        "text": "Derive reciprocity theorem for antennas. Show that the transmitting and receiving radiation patterns of an antenna are equal.",
        "chapter": "2. Radiation of Electric dipole",
        "difficulty": "Hard",
        "raw_matches": [
            ("Winter 2021", 7, "Derive reciprocity theorem for antennas. Show that the transmitting and receiving radiation patterns of an antenna are equal.")
        ]
    },
    "2.7": {
        "text": "Calculate the radiation resistance if the effective height of the aerial is 1/100th of the length of wave emitted.",
        "chapter": "2. Radiation of Electric dipole",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2022", 3, "Calculate the radiation resistance if the effective height of the aerial is 1/100th of the length of wave emitted.")
        ]
    },
    "3.1": {
        "text": "Define the following antenna parameters: Beam solid angle, Directivity, Antenna Aperture, Half Power Beamwidth, Radiation intensity, Antenna radiation efficiency, and Effective length.",
        "chapter": "3. Antenna parameters and definitions",
        "difficulty": "Easy",
        "raw_matches": [
            ("Summer 2022", 3, "Define the following terms: (i) Beam solid angle (ii) Directivity (iii) Antenna Aperture"),
            ("Summer 2023", 7, "Define the following terms. (Draw necessary figures and write equations if any): i) Half Power Beamwidth ii) Radiation intensity iii) Antenna radiation efficiency iv) Effective length"),
            ("Summer 2024", 4, "Define the following terms. (Draw necessary figures and write equations if any): i) Beam solid angle ii) FNBW and HPBW"),
            ("Summer 2025", 3, "Define (1) Antenna, (2) Directivity, (3) Polarization"),
            ("Winter 2025", 3, "Define: 1. Antenna Radiation Efficiency. 2. Radiation Resistance of Antenna. 3. HPBW of Antenna."),
            ("Winter 2021", 3, "Define the following terms: 1. Directivity 2. Radiation Resistance 3. Beam Efficiency"),
            ("Winter 2021", 4, "Explain the concept of polarization for an antenna."),
            ("Winter 2022", 3, "Define the following parameters: (i) Radiation Intensity (ii) Directive Gain and (iii) Radiation Efficiency."),
            ("Winter 2023", 3, "Define a) Directivity b) Effective height c) Solid angle, in context of antenna."),
            ("Winter 2023", 3, "Define Effective aperture. Calculate effective aperture for antenna designed for 125 MHz carrier signal for case a) isotropic antenna b) antenna having directivity 15."),
            ("Winter 2024", 7, "Define the following terms: i) Half Power Beam width ii) Directivity and Gain iii) Radiation resistance iv) Antenna efficiency v) Radiation intensity vi) Beam efficiency"),
            ("Winter 2024", 3, "Describe circular polarization.")
        ]
    },
    "3.2": {
        "text": "Derive the expression of Friis transmission formula and explain how it determines loss between two antennas.",
        "chapter": "3. Antenna parameters and definitions",
        "difficulty": "Hard",
        "raw_matches": [
            ("Summer 2022", 4, "Derive the expression of Friis transmission formula"),
            ("Summer 2024", 7, "How does the Friis transmission theory help to determine loss between the two antennas located in free space? Explain with necessary formula and theory."),
            ("Winter 2021", 7, "Derive the expression of Friss transmission formula."),
            ("Winter 2024", 7, "How does the Friis transmission theory help to determine loss between the two antennas located in free space? Explain with necessary formula and theory."),
            ("Summer 2025", 7, "Derive the expression of Friis Transmission formula. Explain radio communication link between transmitting antenna and receiving antenna."),
            ("Winter 2023", 7, "Derive Friss transmission formula. A radio link has a 30-W transmitter connected to an antenna... find the power delivered...")
        ]
    },
    "3.3": {
        "text": "Enlist and discuss about various antenna field zones with figures.",
        "chapter": "3. Antenna parameters and definitions",
        "difficulty": "Easy",
        "raw_matches": [
            ("Winter 2021", 3, "Discuss antenna field zones."),
            ("Summer 2024", 4, "Enlist and discuss about various antenna field zones with figure."),
            ("Winter 2025", 3, "Explain antenna field zones with necessary figures."),
            ("Winter 2024", 4, "Draw and explain the antenna field zone."),
            ("Summer 2025", 3, "List down antenna radiating regions. What are near field and far field regions?")
        ]
    },
    "3.4": {
        "text": "Derive the relation between Directivity and Beam area.",
        "chapter": "3. Antenna parameters and definitions",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2023", 4, "Derive the relation between Directivity and Beam area.")
        ]
    },
    "3.5": {
        "text": "Differentiate Gain and Directivity.",
        "chapter": "3. Antenna parameters and definitions",
        "difficulty": "Easy",
        "raw_matches": [
            ("Summer 2024", 3, "Differentiate Gain and Directivity.")
        ]
    },
    "3.6": {
        "text": "Find the HPBW, FNBW, beam area, and directivity for given field patterns (e.g., E(theta) = cos^2(theta) or Pn(theta) = cos^3(theta)).",
        "chapter": "3. Antenna parameters and definitions",
        "difficulty": "Hard",
        "raw_matches": [
            ("Summer 2025", 4, "An antenna has a field pattern E(θ) = cos^2 θ , 0 <= θ <= 90°. Find HPBW and FNBW."),
            ("Winter 2023", 4, "1. Find beam area for antenna pattern described by Pn(θ)= cos^3θ. 2. Write expression of finding directivity from solid angle. Calculate directivity of a) isotropic antenna b) antenna having solid angle π/4.")
        ]
    },
    "3.7": {
        "text": "Explain the difference between radian and steradian and show that one steradian is 3282 square degrees.",
        "chapter": "3. Antenna parameters and definitions",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2023", 4, "1) Explain difference between radian and steradian. Show that one steradian is 3282 square degrees.")
        ]
    },
    "3.8": {
        "text": "What do you mean by isotropic radiator? Compare it with omnidirectional radiator.",
        "chapter": "3. Antenna parameters and definitions",
        "difficulty": "Easy",
        "raw_matches": [
            ("Summer 2023", 4, "What do you mean by isotropic radiator? Compare it with omnidirectional radiator.")
        ]
    },
    "3.9": {
        "text": "Derive the mathematical expression for the radiation intensity of an isotropic radiator.",
        "chapter": "3. Antenna parameters and definitions",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2025", 3, "Derive the mathematical expression for the radiation intensity of an isotropic radiator.")
        ]
    },
    "3.10": {
        "text": "Show that the directivity of an infinitesimal dipole is 1.76dB (or 3/2).",
        "chapter": "3. Antenna parameters and definitions",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2025", 4, "Show that the directivity of an infinitesimal dipole is 1.76dB."),
            ("Winter 2022", 7, "Show that the directivity of an electric current element is 3/2 or 1.761 db.")
        ]
    },
    "3.11": {
        "text": "Derive the mathematical expression between maximum effective aperture and directivity.",
        "chapter": "3. Antenna parameters and definitions",
        "difficulty": "Hard",
        "raw_matches": [
            ("Winter 2025", 7, "Derive the mathematical expression between maximum effective aperture and directivity.")
        ]
    },
    "3.12": {
        "text": "Find the directivity and gain when the input power is 125.66 mW and maximum radiation intensity is 200mW/unit solid angle.",
        "chapter": "3. Antenna parameters and definitions",
        "difficulty": "Hard",
        "raw_matches": [
            ("Summer 2022", 3, "The maximum radiation intensity of a 90% efficiency antenna is 200mW/ unit solid angle. Find the directivity and gain (dimensionless and in dB) when the input power is 125.66 mW.")
        ]
    },
    "3.13": {
        "text": "Draw the Radiation Pattern and write the relation between directivity and gain.",
        "chapter": "3. Antenna parameters and definitions",
        "difficulty": "Easy",
        "raw_matches": [
            ("Summer 2025", 4, "(1) Draw the Radiation Pattern and give necessary indications. (2) Write an equation which shows the relation between directivity and gain.")
        ]
    },
    "4.1": {
        "text": "Explain in detail about Binomial array and the principle of pattern multiplication for antenna arrays.",
        "chapter": "4. Arrays of point sources",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 7, "Explain in the detail about Binomial array and pattern multiplication"),
            ("Winter 2021", 7, "State and explain the principle of pattern multiplication for antenna array."),
            ("Summer 2023", 4, "Explain the principal of pattern multiplication for the antenna array."),
            ("Summer 2025", 3, "Explain the principle of pattern multiplication with necessary example"),
            ("Summer 2025", 7, "Write a short note on Binomial array."),
            ("Winter 2025", 4, "Explain the concept of pattern multiplication."),
            ("Winter 2023", 7, "Explain principle of pattern multiplication for array of point sources. Take example of two short dipole and show it with pattern figures. What is significance of Array Factor?"),
            ("Winter 2024", 4, "Discuss Binomial arrays.")
        ]
    },
    "4.2": {
        "text": "Discuss Dolph-Tchebysheff distribution for linear arrays.",
        "chapter": "4. Arrays of point sources",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 4, "Discuss Dolph–Tchebysheff distribution for linear arrays."),
            ("Summer 2024", 7, "Describe the principle of pattern multiplication in the working of array antennas. Explain Dolph-Tchebysheff distribution for linear arrays."),
            ("Winter 2023", 4, "Define steps for designing broadside Dolph -Tchebysheff' array for given ratio of major to minor lobe and spacing.")
        ]
    },
    "4.3": {
        "text": "Explain Schelkunoff theorems for linear arrays and its usefulness.",
        "chapter": "4. Arrays of point sources",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2023", 7, "Explain (i) Schelkunoff theorems for linear arrays (ii) Binomial arrays."),
            ("Summer 2024", 4, "Explain Schelkunoff theorems and its usefulness.")
        ]
    },
    "4.4": {
        "text": "What do you mean by array? Discuss its types in brief.",
        "chapter": "4. Arrays of point sources",
        "difficulty": "Easy",
        "raw_matches": [
            ("Summer 2023", 3, "What do you mean by array? Discuss its types in brief.")
        ]
    },
    "4.5": {
        "text": "Differentiate broadside array and endfire array, and describe their properties.",
        "chapter": "4. Arrays of point sources",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2021", 3, "Differentiate between broadside array and endfire array."),
            ("Summer 2022", 7, "Describe the properties of Endfire array."),
            ("Winter 2025", 3, "Differentiate broadside array and endfire array."),
            ("Winter 2022", 4, "Explain the properties of broadside array.")
        ]
    },
    "4.6": {
        "text": "Derive the expression for the far field pattern of an array of point sources (e.g. 2 isotropic sources fed in-phase or out-of-phase).",
        "chapter": "4. Arrays of point sources",
        "difficulty": "Hard",
        "raw_matches": [
            ("Winter 2022", 7, "Discuss arrays of two point sources with (i) equal amplitude and phase and (ii) Equal amplitude and opposite phase."),
            ("Summer 2023", 4, "Draw field pattern of an array of 4 isotropic point source. Separated by half wave length."),
            ("Summer 2025", 4, "Derive an expression of 2 – isotropic point sources of same amplitude and same phase, placed equi – distance from center axis. Also draw its radiation pattern having distance between two elements as λ/2."),
            ("Winter 2022", 7, "Derive the array factor for N element uniform linear array of equal amplitude and spacing."),
            ("Winter 2024", 7, "Derive the expression for the far field pattern of an array of 2 – isotropic point sources i) Equal amplitude and phase ii) Equal amplitude and opposite phase"),
            ("Summer 2022", 7, "With necessary figure and derivations explain N element array of equal amplitude and spacing. Write the equation for array Factor."),
            ("Winter 2023", 7, "Derive AF (array factor) for N element linear uniform array. Calculate value of progressive phase shift to achieve broadside and end fire antenna array.")
        ]
    },
    "4.7": {
        "text": "Design a linear array with a spacing of d = lambda/6 such that it has zeros at theta = 0, 45, and 90 degrees using Schelkunoff's method.",
        "chapter": "4. Arrays of point sources",
        "difficulty": "Hard",
        "raw_matches": [
            ("Winter 2023", 7, "Design a linear array with a spacing between the elements of d= λ/6 such that it has zeros at θ=0o, 45 o and 90 o. Determine the number of elements, their excitation and plot the received pattern. Use Schelkunoff's method.")
        ]
    },
    "4.8": {
        "text": "Explain the effect of ground on ungrounded antenna.",
        "chapter": "4. Arrays of point sources",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 3, "Explain the effect of ground on ungrounded antenna.")
        ]
    },
    "5.1": {
        "text": "Explain the working principle and radiation resistance of small loop antenna.",
        "chapter": "5. Loop Antenna",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 4, "Explain the working principle of small loop antenna."),
            ("Summer 2023", 4, "Calculate the radiation resistance of a single turn small circular loop having a radius λ/25."),
            ("Summer 2025", 7, "Explain about loop antenna. Explain the working principle of small loop antenna with necessary equations"),
            ("Winter 2025", 7, "Derive the field components of a small loop antenna."),
            ("Winter 2024", 7, "Give an expression of radiation resistance of a small loop.")
        ]
    },
    "5.2": {
        "text": "Derive the directivity of loop antennas for large loop.",
        "chapter": "5. Loop Antenna",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2022", 3, "Derive the directivity of loop antennas for large loop.")
        ]
    },
    "6.1": {
        "text": "Explain helical geometry, pitch angle, axial ratio, modes of radiation, and practical design considerations for helical antennas.",
        "chapter": "6. Helical antenna",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 7, "Explain practical design consideration for the helical antenna."),
            ("Summer 2023", 3, "Define pitch angle and axial ratio for helical antenna."),
            ("Winter 2021", 4, "Describe different modes of propagation of helical antenna."),
            ("Winter 2022", 3, "Explain in brief the two mode of radiation in helix antenna."),
            ("Summer 2024", 4, "Explain the normal mode of radiation of Helical antenna with neat and clean figure."),
            ("Summer 2025", 3, "Explain helical geometry"),
            ("Winter 2025", 7, "Sketch the helical geometry with its associated dimensions showing relationship between circumference, spacing, turn length and pitch angle of helix. Explain the axial mode of helical antenna."),
            ("Winter 2024", 3, "Draw the helical antenna with its associated dimensions showing relationship between circumference, spacing, turn length and pitch angle of helix."),
            ("Winter 2024", 4, "Write the applications of helical antenna.")
        ]
    },
    "7.1": {
        "text": "Explain the construction, operation, and design of Yagi-Uda antenna.",
        "chapter": "7. Arrays of dipoles & apertures",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 4, "Explain the features of Yagi Uda antenna."),
            ("Summer 2023", 3, "Explain construction of 3-element Yagi-Uda antenna with neat and clean figure."),
            ("Summer 2024", 4, "Design 4-element Yagi-Uda antenna."),
            ("Summer 2025", 3, "With suitable diagram discuss the construction features of Yagi-Uda antenna."),
            ("Winter 2025", 4, "Explain 3-element Yagi-Uda antenna."),
            ("Winter 2021", 3, "Explain the working of 3 element Yagi-Uda antenna."),
            ("Winter 2022", 7, "Write short notes on Yagi Uda array antenna."),
            ("Winter 2023", 3, "Draw the structure of 5 element yagi uda antenna. Draw its radiation pattern and provide its properties."),
            ("Winter 2024", 7, "With a suitable diagram, discuss the construction and operation of a Yagi antenna.")
        ]
    },
    "7.2": {
        "text": "Along with necessary figure explain the principle of Folded dipole.",
        "chapter": "7. Arrays of dipoles & apertures",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 4, "Along with necessary figure explain the principle of Folded dipole"),
            ("Summer 2024", 4, "Explain the principle of Folded dipole with figure."),
            ("Winter 2021", 4, "Explain the working of a folded dipole antenna."),
            ("Winter 2022", 3, "Discuss a folded dipole antenna."),
            ("Winter 2025", 3, "Briefly explain folded dipole antenna.")
        ]
    },
    "7.3": {
        "text": "Explain in detail about frequency scanning arrays.",
        "chapter": "7. Arrays of dipoles & apertures",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 7, "Explain in detail about frequency scanning arrays.")
        ]
    },
    "7.4": {
        "text": "Explain various types of antennas with their applications.",
        "chapter": "7. Arrays of dipoles & apertures",
        "difficulty": "Easy",
        "raw_matches": [
            ("Summer 2023", 7, "Explain various types of antennas with their applications.")
        ]
    },
    "7.5": {
        "text": "Describe smart antennas.",
        "chapter": "7. Arrays of dipoles & apertures",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2021", 4, "Describe smart antennas.")
        ]
    },
    "7.6": {
        "text": "Explain Resonant long wire antenna.",
        "chapter": "7. Arrays of dipoles & apertures",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2023", 4, "Explain Resonant long wire antenna. Draw the graph of long wire antenna length versus gain over dipole & Explain it.")
        ]
    },
    "8.1": {
        "text": "Explain Cassegrain feed and list different types of reflector antennas.",
        "chapter": "8. Reflector antennas",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 7, "Explain Cassegrain feed with required figure."),
            ("Summer 2023", 4, "Discuss the different types of reflector antennas."),
            ("Summer 2024", 3, "Explain Cassegrain feed of parabolic reflector."),
            ("Winter 2025", 7, "Write short note on parabolic reflector antenna."),
            ("Winter 2022", 4, "Describe the Cassegrain method of feeding a parabolic reflector."),
            ("Winter 2024", 4, "Explain different types of reflector Antennas.")
        ]
    },
    "8.2": {
        "text": "Calculate the diameter of parabolic dish antenna, for given value of gain G = 40 dB and operating frequency 11 GHz.",
        "chapter": "8. Reflector antennas",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 3, "Calculate the diameter of parabolic dish antenna, for given value of gain G = 40 dB and operating frequency 11 GHz.")
        ]
    },
    "8.3": {
        "text": "Calculate the directivity of an antenna with circular aperture of diameter 3 meter at frequency 5 GHz.",
        "chapter": "8. Reflector antennas",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 3, "Calculate the directivity of an antenna with circular aperture of diameter 3 meter at frequency 5 GHZ.")
        ]
    },
    "8.4": {
        "text": "Explain Feed methods of Parabolic reflectors.",
        "chapter": "8. Reflector antennas",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2025", 7, "Write a short note on (1) Feed methods of Parabolic reflectors and (2) Feed methods of Microstrip Patch Antennas.")
        ]
    },
    "9.1": {
        "text": "State Babinet's principle and illustrate its application to slot antennas and complementary antennas.",
        "chapter": "9. Slot patch & Horn antennas",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 7, "State Babinet's principle and illustrate its application to slot antennas and complementary antennas."),
            ("Summer 2023", 7, "Explain Babinet's Principle. Discuss it for slot and complementary antenna"),
            ("Winter 2021", 3, "Briefly explain Babinet's principle."),
            ("Winter 2025", 4, "Explain Babinet's principle."),
            ("Winter 2023", 4, "Define Babinets' Principle. Explain how this principle can be used in the working of slot antenna."),
            ("Summer 2025", 4, "State Babinet's principle. Explain slot antenna."),
            ("Winter 2024", 3, "Explain Babinet's principle.")
        ]
    },
    "9.2": {
        "text": "Describe various types of basic horns, optimum horn dimensions, and the design steps for a pyramidal horn.",
        "chapter": "9. Slot patch & Horn antennas",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 3, "Describe various types of basic horns with figure."),
            ("Winter 2021", 4, "Describe various types of basic horns with figure."),
            ("Winter 2022", 3, "Explain the function and types of horn antenna."),
            ("Summer 2024", 3, "Enumerate the steps for the design pyramidal horn."),
            ("Summer 2025", 4, "What is the function of horn antenna? List down various horn antennas. Give the optimum horn dimensions.")
        ]
    },
    "9.3": {
        "text": "Find the Capture area for a rectangular horn antenna operating at 2 GHz frequency with a gain of 12 dBi.",
        "chapter": "9. Slot patch & Horn antennas",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2023", 3, "Find the Capture area for a rectangular horn antenna operating at 2 GHz frequency with a gain of 12 dBi.")
        ]
    },
    "10.1": {
        "text": "Describe the working principle, design, feeding methods, and radiation mechanism of microstrip patch antennas.",
        "chapter": "10. Microstrip (patch) antennas",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2023", 7, "Describe the working principle, design and applications of rectangular microstrip patch antenna."),
            ("Summer 2024", 3, "Describe the working principle of Microstrip Patch antenna."),
            ("Winter 2021", 7, "Write short note on microstrip antenna."),
            ("Winter 2022", 4, "Discuss the micro strip patch antenna."),
            ("Winter 2023", 7, "Explain different Feeding methods of Micro strip antenna with diagram."),
            ("Winter 2025", 7, "Write short note on microstrip patch antenna."),
            ("Summer 2025", 4, "Explain in brief radiation mechanism for microstrip patch antenna. Enlist its advantages, disadvantages and applications of microstrip patch antenna."),
            ("Winter 2024", 4, "Explain Microstrip antenna briefly.")
        ]
    },
    "11.1": {
        "text": "Explain Non-metallic Dielectric lens and artificial dielectric lens antennas, their types, advantages, and disadvantages.",
        "chapter": "11. Lens antennas",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 7, "Explain Non-metallic Dielectric lens and artificial dielectric lens antennas in detail."),
            ("Winter 2021", 3, "Briefly explain reflector lens antenna."),
            ("Winter 2022", 4, "Explain the Lens antenna with merits and demerits of lens antenna."),
            ("Winter 2023", 7, "Explain the working of artificial dielectric lens antenna and derive the expression for effective refractive index of a lens formed by conducting sphere."),
            ("Winter 2023", 4, "What is the difference between Reflector antenna and Lens antenna? Explain the concept of Zoning of Lens antenna with equation."),
            ("Summer 2024", 7, "Explain the working of Artificial dielectric Lens antenna and derive the expression for Effective Refractive Index of such a lens formed by conducting sphere."),
            ("Summer 2025", 3, "What is lens antenna? Enlist its advantages and disadvantages."),
            ("Winter 2025", 4, "Briefly explain different types of lens antenna."),
            ("Winter 2024", 3, "Explain Non-metallic dielectric lens antennas.")
        ]
    },
    "12.1": {
        "text": "Explain log-periodic antenna works as frequency independent antenna, and design log periodic dipole array.",
        "chapter": "12. Broadband & Freq. Independent antennas",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 4, "Explain about log periodic antenna with necessary figures."),
            ("Summer 2023", 4, "Explain log-periodic antenna works as frequency independent antenna."),
            ("Winter 2021", 7, "Write short note on log periodic antenna."),
            ("Winter 2022", 7, "Explain with suitable diagram the working of the log periodic antenna. What are the practical applications of these antennas?"),
            ("Winter 2023", 7, "Design a log periodic dipole array to cover the frequency range 54-216 MHz and to have a gain of 8.5 dB. Take σ = 0.149 and τ = 0.822."),
            ("Winter 2025", 7, "Write short note on log periodic antenna with necessary figure."),
            ("Summer 2025", 7, "What do you mean by frequency independent antennas? Draw log periodic wire antenna and explain the functioning and design concepts in detail."),
            ("Winter 2024", 3, "When can an antenna be termed Frequency independent?"),
            ("Winter 2023", 3, "State Rumsey's Principle and discuss the criteria for the antenna to be frequency independent.")
        ]
    },
    "13.1": {
        "text": "Explain in brief about antennas for satellite communication and mobile communication.",
        "chapter": "13. Antennas for special applications",
        "difficulty": "Easy",
        "raw_matches": [
            ("Summer 2023", 3, "Explain in brief about antennas for satellite communication."),
            ("Winter 2025", 3, "Explain in brief about antennas for satellite communication."),
            ("Winter 2024", 4, "Explain in brief about antenna for mobile communication.")
        ]
    },
    "13.2": {
        "text": "Explain the Ultra-wideband antenna (UWB) antenna for Digital application.",
        "chapter": "13. Antennas for special applications",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2024", 4, "Explain the Ultra-wideband antenna (UWB) antenna for Digital application."),
            ("Winter 2021", 3, "Briefly explain ultra wide band antenna."),
            ("Winter 2025", 4, "Briefly explain UWB antenna.")
        ]
    },
    "13.3": {
        "text": "What are the properties of Plasma antenna? Give the working principle of plasma antenna.",
        "chapter": "13. Antennas for special applications",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2022", 3, "Discuss the Plasma antenna."),
            ("Winter 2023", 4, "What are the properties of Plasma antenna? Give the working principle of plasma antenna.")
        ]
    },
    "13.4": {
        "text": "Explain embedded antenna.",
        "chapter": "13. Antennas for special applications",
        "difficulty": "Easy",
        "raw_matches": [
            ("Winter 2024", 4, "Explain embedded antenna.")
        ]
    },
    "14.1": {
        "text": "Explain the experimental setup for the measurement of Gain of antenna under test and enlist antenna gain methods.",
        "chapter": "14. Antennas measurements",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2023", 7, "Explain the experimental setup for the measurement of Gain of antenna under test."),
            ("Winter 2021", 4, "Explain the experimental set up for gain measurement."),
            ("Winter 2022", 4, "Explain the procedure for measurement of the radiation pattern of antenna."),
            ("Winter 2025", 7, "Enlist antenna gain methods and explain any two in detail."),
            ("Winter 2023", 7, "Using friss transmission formula, derive the equation of different methods to measure the Gain of test antenna."),
            ("Summer 2025", 7, "Explain the Gain measurement methods"),
            ("Winter 2024", 7, "Explain the experimental setup for the measurement of radiation pattern of antenna under test.")
        ]
    },
    "14.2": {
        "text": "Describe phase measurement method used in antenna system in detail.",
        "chapter": "14. Antennas measurements",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2024", 7, "Describe phase measurement method used in antenna system in detail."),
            ("Winter 2025", 3, "Explain any one antenna phase measurement method.")
        ]
    },
    "14.3": {
        "text": "Derive the equation of measurement of Impedance of Antenna under test (AUT) using slotted line.",
        "chapter": "14. Antennas measurements",
        "difficulty": "Hard",
        "raw_matches": [
            ("Winter 2023", 4, "Derive the equation of measurement of Impedance of Antenna under test (AUT) using slotted line.")
        ]
    },
    "15.1": {
        "text": "Explain different modes of radio wave propagation (Ground, Sky, Space wave) and their definitions.",
        "chapter": "15. Radio wave propagation",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 4, "Explain the Different modes of Radio wave propagation."),
            ("Summer 2023", 7, "Explain the different modes of radio wave propagation."),
            ("Summer 2024", 7, "Explain the different modes of radio wave propagation."),
            ("Winter 2025", 3, "Enlist different modes of propagation."),
            ("Winter 2022", 7, "Describe the structure of the ionosphere and part played by it in the long distance transmission of radio signals in the HF band."),
            ("Winter 2024", 7, "Explain different modes of propagations in detail."),
            ("Winter 2024", 3, "What is meant by Space Wave?"),
            ("Summer 2025", 4, "Enlist and draw with suitable indications of different modes of propagation.")
        ]
    },
    "15.2": {
        "text": "Explain terms with reference to Wave propagation: Super refraction, Multi hop Propagation, Skip distance, Virtual Height, MUF, critical frequency.",
        "chapter": "15. Radio wave propagation",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 3, "Explain multihop propagation briefly."),
            ("Winter 2021", 7, "Explain terms with reference to Wave propagation phenomenon: 1. Duct propagation 2. Virtual height 3. MUF 4. Skip distance"),
            ("Winter 2022", 7, "Explain the critical frequency and what is the critical frequency for reflection at vertical incidence if the maximum value of electron density is 1.24 x 10^6 cm^-3?"),
            ("Summer 2025", 3, "Define Virtual Height, Maximum Usable Frequency and critical frequency"),
            ("Summer 2025", 3, "Explain Skip distance"),
            ("Winter 2025", 3, "In context of radio wave propagation define: 1. MUF. 2. Skip Distance. 3. Virtual Height."),
            ("Winter 2025", 4, "Explain multi-hop propagation."),
            ("Summer 2024", 7, "Explain terms with reference to Wave propagation phenomenon with necessary figure: (i) Super refraction (ii) Multi hop Propagation (iii) Skip zone"),
            ("Summer 2024", 3, "Describe Surface wave propagation briefly."),
            ("Winter 2024", 4, "Explain the following terms with neat and clean figure: i) Skip distance ii) Multihop propagation"),
            ("Winter 2023", 3, "The observed critical frequencies of E and F layer at Guwahati at a particular times are 2.5 MHz and 8.4 MHz respectively. Calculate the Maximum electron concentration of the layers.")
        ]
    },
    "15.3": {
        "text": "With figure describe the ionization layers and the structure of ionosphere.",
        "chapter": "15. Radio wave propagation",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2022", 4, "With figure describe the ionization layers."),
            ("Winter 2021", 4, "With figure describe the ionization layers."),
            ("Summer 2023", 4, "Explain different layers of ionosphere with neat and clean figure."),
            ("Summer 2025", 4, "Explain the structure of ionosphere.")
        ]
    },
    "15.4": {
        "text": "Define Radio Horizon and Optical Horizon. Derive the equation of effective earth radius with proper diagram.",
        "chapter": "15. Radio wave propagation",
        "difficulty": "Hard",
        "raw_matches": [
            ("Winter 2023", 7, "Define Radio Horizon and Optical Horizon. Derive the equation of effective earth radius with proper diagram.")
        ]
    },
    "15.5": {
        "text": "Define the following terms with figure: i) Duct propagation ii) Linear polarization.",
        "chapter": "15. Radio wave propagation",
        "difficulty": "Medium",
        "raw_matches": [
            ("Summer 2023", 4, "Define the following terms with figure. i) Duct propagation ii) Linear polarization")
        ]
    },
    "15.6": {
        "text": "Define Scattering. Draw the diagram of Tropospheric scatter and explain it.",
        "chapter": "15. Radio wave propagation",
        "difficulty": "Medium",
        "raw_matches": [
            ("Winter 2023", 3, "Define Scattering. Draw the diagram of Tropospheric scatter and explain it.")
        ]
    }
}

# ==============================================================================
# DATASET GENERATION LOGIC
# ==============================================================================

def generate_csv(subject_name, unique_questions, filename):
    filepath = os.path.join("e:\\DATASET\\dataset\\processed", filename)
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Question",
            "Subject",
            "Chapter",
            "Years_Appeared",
            "Frequency",
            "Average_Marks",
            "Difficulty",
            "Priority"
        ])
        
        for q_id, q_data in sorted(unique_questions.items(), key=lambda x: [int(c) for c in x[0].split('.')]):
            raw_occurrences = q_data["raw_matches"]
            semesters = [item[0] for item in raw_occurrences]
            sorted_semesters = sort_semesters(semesters)
            years_appeared_str = ", ".join(sorted_semesters)
            
            frequency = len(raw_occurrences)
            
            marks = [item[1] for item in raw_occurrences]
            avg_marks = round(sum(marks) / len(marks), 2)
            
            # Check consecutive years for priority
            has_consecutive = check_consecutive_semesters(sorted_semesters)
            
            if frequency >= 4 or has_consecutive:
                priority = "High"
            elif frequency in [2, 3]:
                priority = "Medium"
            else:
                priority = "Low"
                
            writer.writerow([
                q_data["text"],
                subject_name,
                q_data["chapter"],
                years_appeared_str,
                frequency,
                avg_marks,
                q_data["difficulty"],
                priority
            ])
    print(f"Generated {filepath} successfully with {len(unique_questions)} unique questions.")

# Generate both datasets
generate_csv("Embedded Systems", es_unique_questions, "embedded_systems_dataset.csv")
generate_csv("Antennas and Propagation", ap_unique_questions, "antennas_and_propagation_dataset.csv")
