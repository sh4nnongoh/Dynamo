// DynamoSandboxManagedWrapper.h


#pragma once
/*
#ifdef DYNAMOSANDBOXMANAGEDWRAPPER_EXPORTS
#define DYNAMOSANDBOXMANAGEDWRAPPER_API __declspec(dllexport)
#else
#define DYNAMOSANDBOXMANAGEDWRAPPER_API __declspec(dllimport)
#endif
*/
using namespace System;
using namespace DynamoSandboxWrapper;

public ref class DynamoSandboxManagedWrapper {
public:
	// Allocate the native object on the C++ Heap via a constructor
	DynamoSandboxManagedWrapper() {

	}

	// Deallocate the native object on a destructor
	~DynamoSandboxManagedWrapper() {
	}

protected:
	// Deallocate the native object on the finalizer just in case no destructor is called
	!DynamoSandboxManagedWrapper() {
	}

public:
	static void Initialize();

private:

};
