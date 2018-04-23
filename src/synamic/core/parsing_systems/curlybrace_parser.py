# lots of thoughts needed.

"""

key1 : value
key2 : {
        multilevel: value 2
        # or it is just a wrapper for multiline value!
        escape literal curly braces with \{ \}
        {{ but this is interpolation }}
}

key3: {!m  # multiline text

}

key4: {  # multivalue
    k1: {
        ! # indentation indicator, otherwise the whole text will taken without stripping
        value
    }
    k2: single line
}

!include values-dev.txt
!include_if_exists values-super-dev2.txt

"""