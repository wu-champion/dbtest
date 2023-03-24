from abc import ABCMeta, abstractmethod
from typing import Any, Set

from .logger import  Logger
from .dataclass import Singleton

class Case(metaclass=ABCMeta):
    def __init__(self, case_id):
        self.logger: Logger = None
        self.case_id = case_id
        self.tags: Set[Tag]= set()

    @abstractmethod
    def run(self) -> bool:...

    @abstractmethod
    def desc(self, desc) -> str:
        '''
        description: describe the case
        return {*}
        '''

    def env(self):
        '''
        description:  return env of the case used
        return {*}
        '''
        return self.env

    def close(self):
        ...

    def add_tag(self, tag):
        self.tags.add(tag)

class Tag:
    def __init__(self, tag_name: Any, level: int=None, parent_tag: 'Tag'=None):
        self.tag_name = tag_name
        self.level = level
        self.child_tags = set()
        self.parent_tags = set()
        self.cases = set()

        if parent_tag:
            self.add_parent_tag(parent_tag)
            parent_tag.add_child_tag(self)

    def __str__(self) -> str:
        return f'{{"Tag.{self.tag_name}_{self.level}}}'

    def __repr__(self) -> str:
        return self.__str__()

    def add_child_tag(self, child: 'Tag'):
        self.child_tags.add(child)
        child.parent_tags.add(self)

    def add_parent_tag(self, parent_tag: 'Tag'):
        self.parent_tags.add(parent_tag)
        parent_tag.child_tags.add(self)

    def delete_child_tag(self, child_tag: 'Tag'):
        self.child_tags.discard(child_tag)
        child_tag.parent_tags.discard(self)

    def delete_parent_tag(self, parent_tag: 'Tag'):
        self.parent_tags.discard(parent_tag)
        parent_tag.child_tags.discard(self)

    def add_case(self, case: Case):
        self.cases.add(case)
        case.add_tag(self)

    def get_parents(self):
        return self.parent_tags

class CaseManage(Singleton):
    def __init__(self, levels: int):
        self.levels = levels
        self.root_tags = [set() for _ in range(levels)]

    def set_tag_level(self, tag: Tag, level: int=0, parent_tag: Tag=None):
        '''
            set a Tag(out of CaseManage) to the CaseManage
        '''
        if level > self.levels - 1 or level < 0:
            raise ValueError(f"tag level must be in set [0, {self.levels}]")

        tag.parent_tags = set()
        tag.child_tags = set()
        tag.level = level

        if level == 0:
            self.root_tags[level].add(tag)
            return

        if not parent_tag or parent_tag not in self.root_tags[level-1]:
            raise ValueError(f"parent_tag must in root_tags[{level-1}]")

        tag.add_parent_tag(parent_tag)
        self.root_tags[level].add(tag)

    def reset_tag_level(self, tag: Tag, level: int = 0, parent_tag: Tag = None) -> None:
        '''
            reset a Tag(in CaseManage) in the CaseManage
        '''
        if level > self.levels - 1 or level < 0:
            raise ValueError(f"tag level must be in set [0, {self.levels}]")

        [p_tag.delete_child_tag(tag) for p_tag in tag.parent_tags]
        [c_tag.delete_parent_tag(tag) for c_tag in tag.child_tags]
        tag.parent_tags = set()
        tag.child_tags = set()

        if level == 0:
            self._set_tag_new_level(tag, level)
            return

        if not parent_tag or parent_tag not in self.root_tags[level-1]:
            raise ValueError(f"parent_tag must in root_tags[{level-1}]")

        tag.add_parent_tag(parent_tag)

        if level == tag.level:
            return

        self._set_tag_new_level(tag, level)

    def _set_tag_new_level(self, tag: Tag, level: int):
        self.root_tags[tag.level].discard(tag)
        self.root_tags[level].add(tag)
        tag.level = level

    def set_case_tag(self, case: Case, tag: Tag):
        case.add_tag(tag)
        tag.add_case(case)

    def set_case_level(self, case: Case, level: int):
        for tag in case.tags:
            if tag.level == level:
                tag.cases.remove(case)
                case.tags.remove(tag)
                break

        self.set_case_tag(case, self.root_tags[level-1])

    def set_case_parent_tag(self, case: Case, parent_tag):
        for tag in case.tags:
            if tag.parent_tag == parent_tag:
                tag.cases.remove(case)
                case.tags.remove(tag)
                break

        self.set_case_tag(case, parent_tag)

    def get_all_tags(self):
        tags = []
        for  tag_level in self.root_tags:
            tags.extend(tag_level)
        return tags

    def get_descendants(self, tag: Tag):
        '''
            return all child-tag of tag, include child-tag of child_tag
        '''
        tags = set()
        for c_tag in tag.child_tags:
            tags.add(c_tag)
            tags.update(self.get_descendants(c_tag))
        return tags

    def get_ancestors(self, tag: Tag):
        '''
            return all parent-tag of tag, include parent-tag of parent_tag
        '''
        tags = set()
        for c_tag in tag.parent_tags:
            tags.add(c_tag)
            tags.update(self.get_ancestors(c_tag))
        return tags

    def get_cases_in_tag(self, tag: Tag):
        return tag.cases

    def get_case_tags(self, case: Case):
        return case.tags