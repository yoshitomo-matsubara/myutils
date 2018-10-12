from common import misc_util


LOSS_DICT = misc_util.get_classes_as_dict('torch.nn.modules.loss')
OPTIM_DICT = misc_util.get_classes_as_dict('torch.optim')


def get_loss(loss_type, param_dict=dict(), **kwargs):
    lower_loss_type = loss_type.lower()
    if lower_loss_type in LOSS_DICT:
        return LOSS_DICT[lower_loss_type](**param_dict, **kwargs)
    raise ValueError('loss_type `{}` is not expected'.format(loss_type))


def get_optimizer(model, optim_type, param_dict=dict(), **kwargs):
    lower_optim_type = optim_type.lower()
    if lower_optim_type in OPTIM_DICT:
        return OPTIM_DICT[lower_optim_type](model.parameters(), **param_dict, **kwargs)
    raise ValueError('optim_type `{}` is not expected'.format(optim_type))
