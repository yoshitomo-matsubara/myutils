import torch


def freeze_module_params(module):
    for param in module.parameters():
        param.requires_grad = False


def unfreeze_module_params(module):
    for param in module.parameters():
        param.requires_grad = True


def extract_decomposable_modules(parent_module, z, module_list, output_size_list=list(), first=True, exception_size=-1):
    parent_module.eval()
    child_modules = list(parent_module.children())
    if not child_modules:
        module_list.append(parent_module)
        try:
            z = parent_module(z)
            output_size_list.append([*z.size()])
            return z, True
        except (RuntimeError, ValueError):
            try:
                z = parent_module(z.view(z.size(0), exception_size))
                output_size_list.append([*z.size()])
                return z, True
            except RuntimeError:
                ValueError('Error w/o child modules\t', type(parent_module).__name__)
        return z, False

    try:
        expected_z = parent_module(z)
    except (RuntimeError, ValueError):
        try:
            resized_z = z.view(z.size(0), exception_size)
            expected_z = parent_module(resized_z)
            z = resized_z

        except RuntimeError:
            ValueError('Error w/ child modules\t', type(parent_module).__name__)
            return z, False

    submodule_list = list()
    sub_output_size_list = list()
    decomposable = True
    for child_module in child_modules:
        z, decomposable = extract_decomposable_modules(child_module, z, submodule_list, sub_output_size_list, False)
        if not decomposable:
            break

    is_tensor = isinstance(expected_z, torch.Tensor)
    if decomposable and is_tensor and expected_z.size() == z.size() and expected_z.isclose(z).all().item() == 1:
        module_list.extend(submodule_list)
        output_size_list.extend(sub_output_size_list)
        return expected_z, True

    if decomposable and not is_tensor and expected_z == z:
        module_list.extend(submodule_list)
        output_size_list.extend(sub_output_size_list)
    elif not first:
        module_list.append(parent_module)
        if is_tensor:
            output_size_list.append([*expected_z.size()])
        else:
            output_size_list.append(len(expected_z))
    return expected_z, True
