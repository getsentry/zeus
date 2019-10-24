from zeus import auth
from zeus.config import db
from zeus.db.utils import create_or_update
from zeus.models import ItemOption

from .base import Resource
from ..schemas import UserSchema

user_schema = UserSchema()


class UserDetailsResource(Resource):
    def get(self, user_id: str):
        """
        Return information on a user.
        """
        if user_id == "me":
            user = auth.get_current_user()
            if not user:
                return self.error("not authenticated", 401)

        else:
            raise NotImplementedError

        user.options = list(ItemOption.query.filter(ItemOption.item_id == user.id))

        return self.respond_with_schema(user_schema, user)

    def put(self, user_id: str):
        """
        Return information on a user.
        """
        if user_id == "me":
            user = auth.get_current_user()
            if not user:
                return self.error("not authenticated", 401)

        else:
            raise NotImplementedError

        result = self.schema_from_request(user_schema, partial=True)
        for name, values in result.get("options", {}).items():
            for subname, value in values.items():
                create_or_update(
                    ItemOption,
                    where={"item_id": user.id, "name": "{}.{}".format(name, subname)},
                    values={"value": value},
                )

        db.session.commit()

        user.options = list(ItemOption.query.filter(ItemOption.item_id == user.id))

        return self.respond_with_schema(user_schema, user)
