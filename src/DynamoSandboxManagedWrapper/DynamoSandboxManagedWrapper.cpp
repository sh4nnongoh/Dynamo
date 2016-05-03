
#include "stdafx.h"

#using "DynamoSandboxWrapper.dll"

#include <msclr\auto_gcroot.h>

using namespace System::Runtime::InteropServices; // Marshal

class DynamoSandboxManagedWrapperPrivate
{
public: msclr::auto_gcroot<DynamoSandboxWrapper::DynamoCSharpWrapper^> dynamoCSharpWrapper;
};

class __declspec(dllexport) DynamoSandboxManagedWrapper
{
private: DynamoSandboxManagedWrapperPrivate* _private;

public: DynamoSandboxManagedWrapper()
{
	_private = new DynamoSandboxManagedWrapperPrivate();
	_private->dynamoCSharpWrapper = gcnew DynamoSandboxWrapper::DynamoCSharpWrapper();
}

public:  void Initialize1()
{
	_private->dynamoCSharpWrapper->Initialize();
	//DynamoSandboxWrapper::DynamoCSharpWrapper::Initialize();
}

public: ~DynamoSandboxManagedWrapper()
{
	delete _private;
}
};