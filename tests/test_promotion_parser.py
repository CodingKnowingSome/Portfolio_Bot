from AA.promotion_parser import parse_promotion_log
import pytest


def test_parse_promotion():
    content = """
    Type: 2
    ```/xp username: KapitanyDrake clloned_jkl action:add value:1```
    ```/lessons username: KapitanyDrake action:Add amount:1```
    """
    result = parse_promotion_log(content)
    assert result.stage == 2
    assert result.usernames == ['KapitanyDrake', 'clloned_jkl']
    assert result.lessons == ['KapitanyDrake']


def test_parse_promotion_missing_type():
    content = "```/lessons username: KapitanyDrake action:Add amount:1```"
    with pytest.raises(ValueError):
        parse_promotion_log(content)


def test_parse_promotion_invalid_type():
    content = """
    Type: a
    ```/xp username: KapitanyDrake clloned_jkl action:add value:1```
    ```/lessons username: KapitanyDrake action:Add amount:1```
    """
    with pytest.raises(ValueError):
        parse_promotion_log(content)


def test_parse_promotion_multiple_users():
    content = """
    Type: 2
    ```/xp username: KapitanyDrake clloned_jkl danni_vxl ryuxwfl action:add value:1```
    ```/lessons username: KapitanyDrake ryuxwfl danni_vxl action:Add amount:1```
    """
    result = parse_promotion_log(content)
    assert result.stage == 2
    assert result.usernames == ['KapitanyDrake', 'clloned_jkl', 'danni_vxl', 'ryuxwfl']
    assert result.lessons == ['KapitanyDrake', 'ryuxwfl', 'danni_vxl']


def test_parse_promotion_correct_full_input():
    content = """
    <@926037474805948416> 
    Host: <@926037474805948416> 
    Co-host: NA
    Type: 3
    Start: 10:15 GMT+2
    End: 10:45 GMT+2
    Attendees: HalloMeMe19191 Dyno
    
    Awarded Points:
    /xp username:HalloMeMe19191 Dyno action:add value:1
    
    Awarded Lessons:
    /lessons username:KapitanyDrake action:Add amount:1
    
    Notes: No image cus no image.
    """
    result = parse_promotion_log(content)
    assert result.stage == 3
    assert result.usernames == ['HalloMeMe19191', 'Dyno']
    assert result.lessons == ['KapitanyDrake']