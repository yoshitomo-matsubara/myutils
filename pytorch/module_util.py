import torch
import torch.nn as nn


def count_params(model):
    return sum(param.numel() for param in model.parameters())


def freeze_module_params(module):
    for param in module.parameters():
        param.requires_grad = False


def unfreeze_module_params(module):
    for param in module.parameters():
        param.requires_grad = True


def extract_target_modules(parent_module, target_class, module_list):
    if isinstance(parent_module, target_class):
        module_list.append(parent_module)

    child_modules = list(parent_module.children())
    for child_module in child_modules:
        extract_target_modules(child_module, target_class, module_list)


def extract_all_child_modules(parent_module, module_list):
    child_modules = list(parent_module.children())
    if not child_modules:
        module_list.append(parent_module)
        return

    for child_module in child_modules:
        extract_all_child_modules(child_module, module_list)


def extract_decomposable_modules(parent_module, z, module_list, output_size_list=None, first=True, exception_size=-1):
    parent_module.eval()
    child_modules = list(parent_module.children())
    if first:
        output_size_list = list()

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

    is_tensor = isinstance(expected_z, torch.Tensor) and isinstance(z, torch.Tensor)
    if decomposable and is_tensor and expected_z.size() == z.size() and expected_z.isclose(z).all().item() == 1:
        module_list.extend(submodule_list)
        output_size_list.extend(sub_output_size_list)
        return expected_z, True

    if decomposable and not is_tensor and type(expected_z) == type(z) and expected_z == z:
        module_list.extend(submodule_list)
        output_size_list.extend(sub_output_size_list)
    elif not first:
        module_list.append(parent_module)
        if is_tensor:
            output_size_list.append([*expected_z.size()])
        else:
            output_size_list.append(len(expected_z))
    elif not isinstance(parent_module, nn.DataParallel) and len(module_list) == len(output_size_list) == 0\
            and len(submodule_list) > 0 and len(sub_output_size_list) > 0:
        module_list.extend(submodule_list)
        output_size_list.extend(sub_output_size_list)
    return expected_z, True
