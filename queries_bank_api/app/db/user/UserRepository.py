from com_ivansoft_corebank_lib.models.User import User as UserModel


class UserRepository:
    def get_by_account_id(self, account_id: str):
        # for hypothetical purposes, we are returning a user with user_id=1 and username='test_user'
        return UserModel(user_id=1, username='test_user')
